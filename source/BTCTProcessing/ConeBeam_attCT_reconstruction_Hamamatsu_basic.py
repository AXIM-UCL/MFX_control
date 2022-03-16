# -*- coding: utf-8 -*-
"""
Created on Tue Mar  1 23:40:55 2022

@author: Carlos Navarrete-Leon
"""

from __future__ import division

import numpy as np
import matplotlib.pyplot as plt
from os import mkdir
from os.path import join, isdir
from imageio import imread, imwrite
import cv2
import astra
#import post_processing
import time

# Configuration.
st_time=time.time()
print('Defining geometry and loading images')
distance_source_origin = 165 # [mm]
distance_source_detector= 700 # [mm]
distance_origin_detector = distance_source_detector-distance_source_origin

M=distance_source_detector/distance_source_origin

detector_pixel_size = 0.05  # [mm]
eff_pix_size=detector_pixel_size/M

detector_rows = 1201  # Vertical size of detector [pixels].
detector_cols = 1501  # Horizontal size of detector [pixels].

pad_x=int((detector_cols-1)/2)
pad_y=int((detector_rows-1)/2)

x_cen = 1254
y_cen = 1018

num_of_projections = 2000
angles = np.linspace(0, 2 * np.pi, num=num_of_projections, endpoint=False)
source=r'D:\Data\22_02_28\CT_2000proj_abs_calib_phantom_big\\'
input_dir = source+'FFC\\'
output_dir = source+'CBReconstructions1254x_1018y_inv\\'
output_sino= source + 'Sinograms\\'

# Load projections.
projections = np.zeros((detector_rows, num_of_projections, detector_cols), dtype=np.float32)
for i in range(num_of_projections):
    file_name='ffc_000'+str(i)+'.tif'
    im = np.flipud(imread(join(input_dir, file_name)))[y_cen-pad_y:y_cen+pad_y+1, x_cen-pad_x:x_cen+pad_x+1]
    im = im/65535
    proj=-np.log(im)
    projections[:, num_of_projections-1-i, :] = proj
    
print('Images loaded. Ellapsted time:', time.time()-st_time)

print('Defining volume and vector geometry')
#%%
# Create the reconstruction volume☺

vol_geom = astra.creators.create_vol_geom(detector_cols, detector_cols, detector_rows)

# Create vector representation projection geometry and 
#copy projection images into ASTRA Toolbox.

proj_geom = astra.create_proj_geom('cone', 1, 1, detector_rows,
                                   detector_cols, angles,
                                   distance_source_origin /
                                   eff_pix_size, 0)

projections_id = astra.data3d.create('-sino', proj_geom, projections)

print('Volume and gometry defined. Ellapsted time:', time.time()-st_time)
print('Reconstructing')
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
print('Reconstruction done. Ellapsted time:', time.time()-st_time)
print('Saving and cleaning')


plt.figure(figsize=(10,10))
plt.imshow(reconstruction[50,:,:], vmin=0.0001)#, vmax=0.075)
plt.colorbar();plt.title('Top Sphere')
plt.figure(figsize=(10,10))
plt.imshow(reconstruction[222,:,:], vmin=0.0001)#, vmax=0.075)
plt.colorbar();plt.title('Central Sphere')
plt.figure(figsize=(10,10))
plt.imshow(reconstruction[340,:,:], vmin=0.0001)#, vmax=0.075)
plt.colorbar();plt.title('Bottom Sphere')
 
#Limit and scale reconstruction.
reconstruction[reconstruction < 0] = 0
middle = detector_rows // 2
maxim = np.max(reconstruction[middle - 400 : middle + 400, :, :])
reconstruction /= maxim
reconstruction[reconstruction > 1] = 1
reconstruction = np.round(reconstruction * 65535).astype(np.uint16)
 
#Save original reconstruction.
if not isdir(output_dir):
    mkdir(output_dir)
for i in range(detector_rows):
    im = reconstruction[i, :, :]
    im = np.flipud(im)
    imwrite(join(output_dir, 'reco%04d.tiff' % i), im)

#Limit and scale projections.
projections[projections < 0] = 0
maxim_proj = np.max(projections[middle - 400 : middle + 400, :, :])
projections /= maxim_proj
projections = np.round(projections * 65535).astype(np.uint16)


#Save sinograms.
if not isdir(output_sino):
    mkdir(output_sino)
for i in range(detector_rows):
    im = projections[i, :, :]
    im = np.flipud(im)
    imwrite(join(output_sino, 'sino%04d.tiff' % i), im)

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
file.write("Source folder: "); file.write(source+"\n")


file.close()

print('Done, Ellapsted time:', time.time()-st_time)