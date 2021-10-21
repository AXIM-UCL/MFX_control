import os
import tifffile
import numpy

from . import _PEPIDetector

class PEPIVirtualDetector(_PEPIDetector._PEPIDetector):
	""" Interface for classes implementing a detector.
	"""

	def __init__(self):
		"""		
		Class constructor
		"""
				
		# Call parent's constructor:
		super().__init__()

		# Flag for initialization done:
		self._initialization_done = False

		# Parameters:
		self._shots = 1


	def initialize(self):
		"""Perform once-for-all initialization operations."""
				
		if not self._initialization_done:

			# Flag for initialization done:
			self._initialization_done = True

		else:
			raise Exception("Virtual detector already initialized. Call terminate() first.") 

	def terminate(self):
		"""Perform once-for-all closing operations."""
		
		if self._initialization_done:
			
			# Flag for initialization done (this terminates the polling thread):
			self._initialization_done = False

		else:
			raise Exception("Virtual detector not initialized. Call initialize() first.") 

	def send_command(self, command: str):
		"""Send low-level command to the device (check device manual)."""
		
		if self._initialization_done:

			# An empty string is returned:
			return ""

		else:
			
			raise Exception("Virtual detector not initialized. Call initialize() first.") 

	def set_param(self, param, value):
		"""Set detector specific parameter."""
		
		# Nothing to do:
		if param == "SHOTS":
			self._shots = int(value)


	def get_param(self, param):
		"""Get detector specific parameter."""
		
		# Nothing to do:
		pass

	def acquire(self, **kwargs):
		"""Perform an acquisition."""
		
		# Fake image is returned:
		curr_path =  os.path.dirname(os.path.abspath(__file__))
		file = os.path.join(curr_path, 'ronnie.tif')
				
		im = tifffile.imread(file).astype(numpy.float32)
		
		out_im1 = numpy.zeros( (im.shape[0],im.shape[1], self._shots), dtype=numpy.uint16 )
		out_im2 = numpy.zeros( (im.shape[0],im.shape[1], self._shots), dtype=numpy.uint16 )

		for i in range(self._shots):
			
			# Add some random noise:
			mean = 0
			var = 100

			gauss = numpy.random.normal(mean,var**0.5,im.shape)
			gauss = gauss.reshape(im.shape)
			im1 = (im + gauss)
			im1[ im1 < 0] = 0
			im1 = im1.astype(numpy.uint16)	
		
			gauss = numpy.random.normal(mean,var**0.5,im.shape)
			gauss = gauss.reshape(im.shape)
			im2 = (im + gauss)
			im2[ im2 < 0] = 0
			im2 = im2.astype(numpy.uint16)

			out_im1[:,:,i] = im1
			out_im2[:,:,i] = im2[:,::-1]

		return numpy.squeeze(out_im1), numpy.squeeze(out_im2)

	def serialize(self):
		"""Prepare a dictionary with object status."""
		
		# Creating a dictionary:
		dict = {"Detector":"Virtual"}

		return dict