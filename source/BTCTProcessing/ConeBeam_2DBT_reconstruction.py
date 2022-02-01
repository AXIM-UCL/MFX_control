# -*- coding: utf-8 -*-
"""
Created on Sat Oct 30 14:15:38 2021

@author: Carlos Navarrrete-Leon
"""

from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
from os import mkdir
from os.path import join, isdir
from imageio import imread, imwrite
import cv2
import astra
import post_processing
import tifffile

# Configuration.

distance_source_origin = 187 # [mm]
distance_source_detector= 866 # [mm]//
distance_origin_detector = distance_source_detector-distance_source_origin

M=distance_source_detector/distance_source_origin

detector_pixel_size = 0.062  # [mm]

tot_dith_steps=8
num_dith_y=8
num_dith_x=8
n_ap_x=54
n_ap_y=42
period=100e-3

M_mask=5.6
sample_period=period*M_mask/M
bt_pix_size=period/num_dith_x*M_mask
eff_pix_size=bt_pix_size/M


channel=1 #1 Att, 2 Phase

detector_rows = n_ap_y*num_dith_y  # Vertical size of detector [pixels].
detector_cols = n_ap_x*num_dith_x  # Horizontal size of detector [pixels].

x_cen = 217
y_cen = 168

deltaU=(detector_cols/2-x_cen)
deltaV=(detector_rows/2-y_cen)
eta=np.radians(0)#Rotation axis tilt

#eta=np.radians(0) #In plane rotation(skew)
theta=np.radians(0) # Out-of-plane rotation (tilt)
phi=np.radians(0) # Out-of-plane rotation (slant)


num_of_projections = 900
angles = np.linspace(0, 2 * np.pi, num=num_of_projections, endpoint=False)
source=r'C:\Data\21_10_29\2BTCT_900proj_aesophagaeus_native20\\'
input_dir = source+'Projections\\'

if(channel==1):
    output_dir = source+'CBReconstructions_Att'
    output_sino = source + 'Sinograms_Att'

if(channel==2):
    output_dir = source+'CBReconstructions_Phase'
    output_sino = source + 'Sinograms_Phase'

correct_xy=0
correct_rings=0

x_disp=np.zeros(900)
y_disp=np.zeros(900)


if(correct_xy):
    x_disp=np.loadtxt(r'C:\Data\21_06_24\x_disp2.txt')*8/9.1
    #y_disp=np.loadtxt(r'C:\Data\21_06_24\y_disp.txt')
    output_dir = output_dir+'_xdrift'
    output_sino += '_xdrift'
    
# Load projections.
projections = np.zeros((detector_rows, num_of_projections, detector_cols), dtype=np.float32)
#projections_phase = np.zeros((detector_rows, num_of_projections, detector_cols), dtype=np.float32)
for i in range(num_of_projections):
    if(channel==1):
        file_name=input_dir+'proj_abs_000'+str(i)+'.tif'
        im_abs=tifffile.imread(file_name)
        projections[:, i, :] = -np.log(im_abs)
    
    elif(channel==2):
        file_name=input_dir+'proj_phase_000'+str(i)+'.tif'
        im_phase=tifffile.imread(file_name)
        projections[:, i, :] = im_phase

# Create the reconstruction volume

vol_geom = astra.creators.create_vol_geom(detector_cols, detector_cols, detector_rows+2*int(abs(deltaV)))

# Vectors

S_vecs=np.zeros((num_of_projections, 3))
D_vecs=np.zeros((num_of_projections, 3))
U_vecs=np.zeros((num_of_projections, 3))
V_vecs=np.zeros((num_of_projections, 3))

M_rotx = np.float32([
    [1, 0, 0],
 	[0, np.cos(eta), np.sin(eta)],
 	[0, -np.sin(eta), np.cos(eta)],    
])

M_roty = np.float32([
 	[np.cos(theta), 0, -np.sin(theta)],
    [0, 1, 0],
 	[np.sin(theta), 0, np.cos(theta)],    
])

M_rotz = np.float32([
 	[np.cos(phi), np.sin(phi), 0], 
 	[-np.sin(phi), np.cos(phi), 0],
    [0, 0, 1]
])

M_rot = np.dot(np.dot(M_rotz, M_roty), M_rotx)

for i in range(len(angles)):
    
    # source
    S_vecs[i,:] = np.array([np.sin(angles[i]), -np.cos(angles[i]), 0]) * (distance_source_origin/eff_pix_size)
    # center of detector
    D_vecs[i,:] = np.array([- np.sin(angles[i]), np.cos(angles[i]), 0]) * (distance_origin_detector/eff_pix_size)
    # vector from detector pixel (0,0) to (0,1)
    U_vecs[i,:]=np.array([np.cos(angles[i]), np.sin(angles[i]), 0]) * (bt_pix_size/eff_pix_size)
    # vector from detector pixel (0,0) to (1,0) 
    V_vecs[i,:]=np.array([0, 0,  bt_pix_size/eff_pix_size])
    
    # Vector Transformations
    S_vecs[i,:] = S_vecs[i,:] - np.array([x_disp[i], 0, 0])
    D_vecs[i,:] = D_vecs[i,:] + deltaU * U_vecs[i,:] + deltaV * V_vecs[i,:] - np.array([x_disp[i], 0, 0])
    U_vecs[i,:] = np.dot(M_rot, U_vecs[i,:])
    V_vecs[i,:] = np.dot(M_rot, V_vecs[i,:])
    

# Vectors matrix
vecs = np.zeros((num_of_projections, 12))

vecs[:, :3] = S_vecs
vecs[:, 3:6] = D_vecs
vecs[:, 6:9] = U_vecs
vecs[:,9:] = V_vecs

# Create vector representation projection geometry and 
#copy projection images into ASTRA Toolbox.

proj_geom = astra.create_proj_geom('cone_vec', detector_rows, detector_cols, vecs)

projections_id = astra.data3d.link('-sino', proj_geom, projections)#ation available 
#projections_id = astra.data3d.link('-sino', proj_geom, projections_phase)

# Create reconstruction.

reconstruction_id = astra.data3d.create('-vol', vol_geom, data=0)

alg_cfg = astra.astra_dict('FDK_CUDA')
alg_cfg['ProjectionDataId'] = projections_id
alg_cfg['ReconstructionDataId'] = reconstruction_id
alg_cfg['option'] = {}
alg_cfg['option']['ShortScan'] = False
algorithm_id = astra.algorithm.create(alg_cfg)

astra.algorithm.run(algorithm_id, 1)

reconstruction = astra.data3d.get(reconstruction_id)

reconstruction[reconstruction < 0] = 0


plt.figure(figsize=(10,10))
plt.imshow(reconstruction[35,:,:])#, vmin=0.0001)#, vmax=0.075)
plt.colorbar();plt.title('Top Sphere')
plt.figure(figsize=(10,10))
plt.imshow(reconstruction[165,:,:])#, vmin=0.0001)#, vmax=0.075)
plt.colorbar();plt.title('Central Sphere')
plt.figure(figsize=(10,10))
plt.imshow(reconstruction[312,:,:])#, vmin=0.0001)#, vmax=0.075)
plt.colorbar();plt.title('Bottom Sphere')


#Save original reconstruction.
if not isdir(output_dir):
    mkdir(output_dir+'//')
for i in range(detector_rows+2*int(abs(deltaV))):
    im = reconstruction[i, :, :]
    im = np.flipud(im)
    imwrite(join(output_dir+'//', 'reco%04d.tif' % i), im.astype(np.float32))

#Correct ring artifacts and save in a different folder
if (correct_rings):
    output_dir = output_dir+'rings'
    if not isdir(output_dir):
        mkdir(output_dir+'//')
    for i in range(detector_rows+2*int(abs(deltaV))):
        im = reconstruction[i, :, :]
        im = np.flipud(im)
        im_corr=post_processing.correct_rings(im, N_lp=121, N_hp=25)
        imwrite(join(output_dir+'//', 'reco%04d.tif' % i), im_corr.astype(np.float32))

#Save sinograms.
if not isdir(output_sino):
    mkdir(output_sino)
for i in range(detector_rows):
    im = projections[i, :, :]
    im = np.flipud(im)
    imwrite(join(output_sino, 'sino%04d.tif' % i), im.astype(np.float32))

# Cleanup.
astra.algorithm.delete(algorithm_id)
astra.data3d.delete(reconstruction_id)
astra.data3d.delete(projections_id)

    
########## ---------- Information file -----------###############

file = open(output_dir+"info_reconstruction.txt","a")

file.write("Zso (mm): "); file.write(str(distance_source_origin)+"\n")
file.write("Zsd (mm): "); file.write(str(distance_source_detector)+"\n")
file.write("Zod (mm): "); file.write(str(distance_origin_detector)+"\n")
file.write("Magnification: "); file.write(str(M)+"\n")
file.write("Pixel size: "); file.write(str(detector_pixel_size)+"\n")
file.write("Detector rows: "); file.write(str(detector_rows)+"\n")
file.write("Detector Columns: "); file.write(str(detector_cols)+"\n")
file.write("X center: "); file.write(str(x_cen)+"\n")
file.write("Y center: "); file.write(str(y_cen)+"\n")
file.write("Eta (radians): "); file.write(str(eta)+"\n")
file.write("Theta (radians): "); file.write(str(theta)+"\n")
file.write("Phi (radians): "); file.write(str(phi)+"\n")
file.write("Source folder: "); file.write(source+"\n")
file.write("Correct XY: "); file.write(str(correct_xy)+"\n")
file.write("Correct Rings: "); file.write(str(correct_rings)+"\n")

file.close()