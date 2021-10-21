import json
import os
import numpy as np
import tifffile
import threading
import queue


class PEPITIFFWriter(object):
	""" Class for synchronous/asynchronous saving to disk in TIFF format with metadata.
	"""

	def __init__(self, path):
		
		self._path = path
		self._asynch = asynchronous

		# Buffer of file to save an process to disk:
		self._queue = queue.Queue()

		# Counters:
		self._flat_ct = 0
		self._tomo_ct = 0

		# Start the consumer thread:
		self._do_consumer = True
		self._consumer = threading.Thread(target=self.__consumer, args=(im, filename, metadata))
		self._consumer.start()


	def __consumer(self):
		
		while self._do_consumer:
			try:
				# Attempt to get data from the queue. This will block thread's 
				# execution until data is available:
				data = self._queue.get()

				# Do the processing of the data and save:

				# Remove the first two defective columns:
				ff_low[:,0,:] = ff_low[:,2,:]
				ff_low[:,1,:] = ff_low[:,2,:]


			except queue.Empty:
				pass
	

	def __save(self, im, filename, metadata):

		# If multidimensional image:
		if (im.ndim == 3):
			# Change order of dimension to match TIFFFile order:
			im = np.transpose(im, (2, 0, 1))

		# Write data and metadata:
		tifffile.imsave(filename, im, description=metadata )				
		

	def save_flat(self, im, metadata):
		
		# Put into queue:
		filename = self._flat_prefix + "_" + str(self._flat_ct).zfill(4)
		self._queue.put(im, filename, metadata)

		# Increment counter:
		self._flat_ct = self._flat_ct + 1
		
		# Add to array of flat images:

		#if self._asynch:
		#	t = threading.Thread(target=self.__save, args=(im, filename, metadata))
		#	t.start()
		#else:
		#	self.__save(im, filename, metadata_list)

	def save_tomo(self, im, filename, metadata):

		if self._asynch:
			t = threading.Thread(target=self.__save, args=(im, filename, metadata))
			t.start()
		else:
			self.__save(im, filename, metadata_list)



class PEPITIFFReader(object):

	def __init__(self):
		pass

	def read(self, filename):

		with tifffile.TiffFile(filename) as tif:
			data = tif.asarray()
			metadata = tif[0].image_description
			metadata = json.loads(metadata.decode('utf-8'))

		return data, metadata
