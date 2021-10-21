import json
import os

import numpy as np
import tifffile
import threading


class PEPITIFFWriter(object):
	""" Class for synchronous/asynchronous saving to disk in TIFF format with metadata.
	"""

	def __init__(self, asynchronous=True):

		self._asynch = asynchronous

	def __save(self, im, filename, metadata_list=()):

		# If multidimensional image:
		if (im.ndim == 3):
			# Change order of dimension to match TIFFFile order:
			im = np.transpose(im, (2, 0, 1))

		# Format metadata into a JSON string:
		metadata = ''
		for item in metadata_list:
			metadata += json.dumps(item.serialize())

		# Write data and metadata:
		tifffile.imsave(filename, im, description=metadata)	
	


	#def __save(self, im, filename, metadata_list=()):

	#	# If multidimensional image:
	#	if (im.ndim == 3):
	#		# Change order of dimension to match TIFFFile order:
	#		im = np.transpose(im, (2, 0, 1))

	#	# Format metadata into a JSON string:
	#	metad = ''
	#	for item in metadata_list:
	#		metad += json.dumps(item.serialize())

	#	# Write data and metadata:
	#	tifffile.imsave(filename, im, imagej=True, metadata={'axes': 'TYX'} )
		
	#	# Prepare metadata text file:
	#	outname = os.path.splitext(filename)[0] + ".json"
	#	with open(outname, 'w') as outfile:
	#		outfile.write(metad)


		

	def save(self, im, filename, metadata_list=()):

		if self._asynch:
			t = threading.Thread(target=self.__save, args=(im, filename, metadata_list,))
			t.start()
		else:
			self.__save(im, filename, metadata_list)



class PEPITIFFReader(object):

	def __init__(self):
		pass

	def read(self, filename):

		with tifffile.TiffFile(filename) as tif:
			data = tif.asarray()
			
			tif_tags = {}
			for tag in tif.pages[0].tags.values():
				name, value = tag.name, tag.value
				if name == "ImageDescription":
					break

			metadata = value

		return data, metadata
