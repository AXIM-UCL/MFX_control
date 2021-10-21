class _PEPIDetector(object):
	""" Interface for classes implementing a detector.
	"""
	def __init__(self):
		""" Class constructor """

		# Current image(s) (for e.g. "live" mode):
		self.image = None

	def initialize(self):
		"""Perform once-for-all initialization operations."""
		pass

	def terminate(self):
		"""Perform once-for-all closing operations."""
		pass

	def send_command(self, command: str):
		"""Send low-level command to the device (check device manual)."""
		pass

	def set_param(self, param: str, value):
		"""Set detector specific parameter."""
		pass

	def get_param(self, param: str):
		"""Get detector specific parameter."""
		pass

	def acquire(self, **kwargs):
		"""Acquire an image."""
		pass

	def serialize(self):
		"""Prepare a string with object status."""
		pass

