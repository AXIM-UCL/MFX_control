
#
# Author: Francesco Brun
# Last modified: April, 14th 2021
#
import numpy as np
import copy
from . import _nanmedfilt2 


def nanmedfilt(im, n):
	""" 2D median filtering by excluding NaNs and Infs.

	Parameters
	----------
	im : array_like
		The 2D image to process.
		
	n : int
		Size of the n x n neighborhood.

	Return value
	------------
	im : array_like
		Filtered 2D image.

	"""		

	arg = np.asfortranarray(im)				# don't forget this line!!
	out = _nanmedfilt2.nanmedfilt2(arg,n)

	return out

def custom_despeckle(arg, flat, flat_filt, n=5, k=3.5):
	""" Apply flat fielding plus outlier correction to a single 2D image
	
	Parameters
	----------
	im : array_like
		The (dark-corrected) projection 2D image to process.
		
	flat : array_like
		Flat field (high-statistics) 2D image.

	flat_filt : array_like
		Filtered flat field 2D image.

	win_size : int
		Size of the median filtering used to compensate outliers (default = 5).
		Higher values means more smoothing.

	k : float
		Adaptive coefficient used to compensate outliers (default = 3.5). Lower
		values means more smoothing.

	Return value
	------------
	im : array_like
		Corrected 2D image.

	"""		
	# Copy:
	im = copy.deepcopy(arg)

	# Remove the first two defective columns:
	im[:,0] = im[:,2]	
	im[:,1] = im[:,2]

	# Ignore division by zero:
	with np.errstate(divide='ignore', invalid='ignore'):

		# Local sigma estimation formula:
		s = np.sqrt(nanmedfilt(im,n)) / flat_filt	
	
		# Standard flat fielding (NaNs and Infs remain):
		out = (im / flat).astype(np.float32)	

		# Mark pixels where |vi-m| > k*s as NaNs:
		tmp = (np.fabs(out - nanmedfilt(out,n)) > (k * s))
		out[tmp] = np.nan

		# Replacement of the NaNs, Infs and values that do not meet |vi-m| < k*s:
		tmp = nanmedfilt(out,n)
		out[np.logical_not(np.isfinite(out))] = tmp[np.logical_not(np.isfinite(out))]
	
	# Return corrected projection:
	return out


def flat_fielding(im, ff, win_size=5, k=3.5):
	""" Apply flat fielding plus outlier correction to the whole input 3D dataset.
	
	Parameters
	----------
	im : array_like
		The (dark-corrected) projection images to process.
		
	ff : array_like
		Flat field images.

	win_size : int
		Size of the median filtering used to compensate outliers (default = 5).
		Higher values means more smoothing.

	k : float
		Adaptive coefficient used to compensate outliers (default = 3.5). Lower
		values means more smoothing.

	Return value
	------------
	im : array_like
		Flat-corrected projections.

	"""				
	# Cast the input image:
	im = im.astype(np.float32)
	ff = ff.astype(np.float32)

	# Remove the first two defective columns:
	ff[:,0,:] = ff[:,2,:]
	ff[:,1,:] = ff[:,2,:]

	# Median along third dimension for the flat image:
	ff = np.nanmedian(ff, axis=2)

	# Get also the median of each win_size:
	ff_filt = nanmedfilt(ff, win_size)

	# For each projection:
	for i in range(0,im.shape[2]):

		im[:,:,i] = custom_despeckle(im[:,:,i], ff, ff_filt, win_size, k)		

	# Return pre-processed image:
	return im.astype(np.float32)