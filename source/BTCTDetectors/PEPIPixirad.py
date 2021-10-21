import subprocess 
import time
import socket
import threading
import struct
import numpy
import copy
import os

from . import _PEPIDetector

class _TCPCommunication(object):
	""" Class responsible for the communication to/from the device. Pixirad assumes
		data communication via TCP socket. Text and binary responses are handled
		according to the Pixirad "protocol".
	"""

	def __init__(self, server_IP, server_TCP_port):
		""" Class constructor. 

			A TCP socket to connect to the specified (server,port) is created.
		"""

		try:
			self._address = server_IP
			self._port = server_TCP_port

			self._timeout = 20 # default

			self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self._sock.connect((self._address, self._port))				
			self._sock.settimeout(self._timeout)

		except:

			# Close TCP Connection to the detector:
			if hasattr(self, '_sock'):
				if self._sock is not None:
					self._sock.close()

			raise RuntimeError("ERROR: Connection to the detector not available. Check network and cable settings.")

	def __del__(self):
		""" Class destructor.
		"""
		# Close connections to the detector:
		if hasattr(self, '_sock'):
			if self._sock is not None:
				self._sock.shutdown(socket.SHUT_RDWR)
				self._sock.close()
				self._sock = None


	def restart(self):
		""" Restart the connection to the Pixirad server. """
		try:
			if self._sock is not None:
				self._sock.shutdown(socket.SHUT_RDWR)				
				self._sock.close()
				self._sock.__del__()
		except:
			pass

		self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.connect((self._address, self._port))		

		self._sock.settimeout(self._timeout)
		

	def settimeout(self, time_s):
		""" Change socket time-out.	"""

		self._timeout = time_s
		self._sock.settimeout(self._timeout)

	def send(self, msg):
		""" Send a message through the TCP socket. For each message 
			a 4-byte length (network byte order) prefix is added.
		"""
		
		msg = struct.pack('<L', len(msg)) + msg.encode('utf-8')
		self._sock.sendall(msg)

	def _recvall(self, n):
		# Helper function to recv n bytes or return None if EOF is hit
		data = bytearray()
		while len(data) < n:
			packet = self._sock.recv(n - len(data))
			if not packet:
				return None
			data.extend(packet)
		return data

	def recv_raw(self):
		""" Receive a message after a previously sent by invoking send(). This
			function receive the raw message from the detector. A bytearray() 
			object is returned.
		"""
		
		# Read message length and unpack it into an integer
		raw_msglen = self._recvall(4)
		if not raw_msglen:
			return None
		msglen = struct.unpack('<L', raw_msglen)[0] # Little-endiand unsigned long
		
		# Read the message data
		return self._recvall(msglen)

	def recv_string(self):
		""" Receive a message after a previously sent by invoking send(). This
			function receive the raw message from the detector and returns a
			string object. Use this method when the expected detector's response
			is an acknowledged string or similar.
		"""
		
		# Read message length and unpack it into an integer
		raw = self.recv_raw()
		
		# Get the length of the string message (in bytes):
		strlen = struct.unpack('<L',  raw[0:4])[0] # Little-endiand unsigned long

		# Skip first four bytes and then convert it as string:
		str_b = raw[4:strlen + 4]

		return str(str_b)

	def recv_image(self):
		""" Receive a binary image or return None in case of timeout. A string 
		describing the image is returned as well as the binary data.

		"""
		
		try:

			str_b = None
			byt_img = None	
		
			# Read total message length (string + binary) and unpack it into an integer:
			raw_msglen = self._recvall(4)
			if not raw_msglen:
				return None
			totlen = struct.unpack('<L', raw_msglen)[0] # Little-endiand unsigned long

			# Read total string length and unpack it into an integer:
			raw_msglen = self._recvall(4)
			if not raw_msglen:
				return None
			strlen = struct.unpack('<L', raw_msglen)[0] # Little-endiand unsigned long

			# Read the string:
			byt_str = self._recvall(strlen)

			# Skip first four bytes and then convert it as string:
			str_b = str(byt_str[4:strlen + 4])

			# Read the image binary data:
			byt_img = self._recvall(totlen - (strlen + 4))

		except Exception as e:

			# Probably this warning can be skipped.
			print("Errors in recv_image(): " + str(e) + ". None return. Consider re-acquire the image.")
			pass
			
		finally:

			# Return the message and the binary data:
			return str_b, byt_img

	

class PEPIPixieIII(_PEPIDetector._PEPIDetector):
	""" Driver for Pixirad-1 | Pixie-III.

	Here is a simple example about how to use this class: ::
		
		from PEPIControl.PEPIDetectors.PEPIPixirad import PEPIPixieIII
		import matplotlib.pyplot as plt

		try:
			det = PEPIPixieIII()

			det.initialize()		
		
			det.set_param("E0_KEV",10.0)
			det.set_param("E1_KEV",37.4)
			det.set_param("EXP_TIME_MILLISEC",1000)
						
			low, high = det.acquire()	

			# Display with matplotlib:
			fig, (ax1, ax2) = plt.subplots(1, 2)
			
			ax1.imshow(low, cmap='gray', vmin=0, vmax=1000)
			ax1.set_title('Image [10.0 - 37.4] keV')
		
			ax2.imshow(high, cmap='gray', vmin=0, vmax=1000)
			ax2.set_title('Image [37.4 - Inf] keV')

			plt.show()

		except Exception as e:
			print("Something went wrong: " + str(e))

		finally:		
			det.terminate()

	"""



	def __init__(self, ip_address='localhost', tcp_port=6666, udp_port=2224):
		"""	The class constructor defines the connection to the device through
			an Ethernet interface. At the best of our knowledge, the detector network 
			address is 196.168.0.1/24 and it cannot be modified. It is configured
			to reply to messages received via TCP port 2222. Moreover, the detector 
			continously send "meteo" information as a broadcast message to the same 
			subnet via UDP port 2224.

			The detector itself outputs the acquired raw images as UDP datagram over
			the port 2223. However, this class is based on a local "forwarding" software 
			delivered together with the original software for Pixirad. This software 
			has to be configured as described by the manufacturer (basically the 
			environment variable PXRDX_ROOT needs to be set and PIXIRAD_SERVER.bat needs 
			to run correctly). In this case ``ip_address`` has to be 127.0.0.1 and the 
			local forwarding server outputs (calibrated) images over TCP port 6666.

			.. note::
			   Check firewall settings to be sure to send/receive messages to/from the 
			   private network 196.168.0.0/24.

			.. note::
			   This version works only on Windows.

			.. note::
			   Network card needs to be configured to maximize throughput over UDP. 
			   Configuration parameters appear under Device Manager >> Network Adapters:


			   .. image:: network_card.jpg
				  :width: 400


			   Suggested options are:


			   - Set Receive Buffer to e.g. 2048 (or any allowed value greater than 1490)
			   - Disable Flow Control
			   - Set Speed & Duplex to the highest possible speed in the full duplex mode
			   - Disable Interrupt Moderation Rate
			   - Disable UDP Checksum offload
			   - Assign Transmit Buffer to the greatest allowed value


		  
		"""

		# Call parent's constructor:
		super().__init__()

		try:

			# This makes sense only for the Windows version of the driver:
			#self._srv_path = os.path.join(os.environ["PXRDX_ROOT"], "PIXIRAD_SERVER.bat")
			#self._server = subprocess.Popen(self._srv_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
			#time.sleep(3)


			# Set the network connections to the server.  For TCP communication
			# there is a specific class.  UDP conversation is simple so all the
			# low-level objects are here.
			self._TCPSocket = _TCPCommunication(ip_address, tcp_port)

			self._server_UDP_port = udp_port			
			self._UDPSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
			self._UDPSocket.bind(('', self._server_UDP_port))		
			

						
			# Set default flags:
			self._init_done = False
			self._poll = False

			# Set dimension:
			self._width = 1024
			self._height = 402
					
			# Safety thresholds:
			self._humidity_threshold = 0.8  # [%] Below this value is OK to thermalize (< 0.1).
											# NOTE: if you put exactly 1.0 it might happen that
                                 			# the Peltier does not start because humidity might
                                 			# fluctuate above 1.0 and then the Peltier automatically
                                 			# stops.
			self._temp_ON_threshold = -18.0 # [C] Below this temperature is OK to acquire -20.0
			self._temp_OFF_threshold = 10.0 # [C] Above this temperature is OK to switch off 10.0


			# Init read-only parameters:
			self._tcold = 0.0
			self._thot = 0.0
			self._hv = 0.0
			self._hv_current = 0.0
			self._box_hum = self._humidity_threshold
			self._box_temp = 0.0
			self._peltier_pwr = 0.0
			self._firmware = ''
			self._info = ''


			# Set defaults for surely varying parameters:
			self._mode = "NPISUM"  # { NONPI | NPI | NPISUM }
			self._col = "2COL"     # { DTF | 1COL0 | 1COL1 | 2COL }
			self._E0 = 5.0         # [keV]
			self._E1 = 35.0        # [keV]
			self._vt_hit = 3.0     # [keV]
			self._shots = 1		   
			self._exp_time = 1000  # [ms]
			self._TCPSocket.settimeout(max(20,int((self._exp_time/1000)*2)))
			self._exp_delay = 0    # [ms]
		
			# Set defaults for almost constant parameters:
			self._trigger = "INT"      # { INT | EXT1 | EXT2 }
			self._bias_mode = "AUTOHV" # { AUTOHV | AUTOHV_LC | AUTOHV_LC | STDHV }
			self._bias_TOnDelay = 1.0  # [s]
			self._bias_TOffDelay = 4.0 # [s]
			self._bias_HVCycle = 5     

			# Prepare output datasets: (in case of image acquisition):
			self._low = numpy.array([], dtype=numpy.uint16)     # 3D dataset when SHOTS > 1
			self._high = numpy.array([], dtype=numpy.uint16)	# 3D dataset when SHOTS > 1		
			
			# Inherited from parent class for future e.g. "live" monitor.
			self.image = numpy.zeros((self._height, self._width, 2), dtype='<u2')

		except:

			# Close connections to the detector:
			if hasattr(self, '_TCPSocket'):
				if self._TCPSocket is not None:
					self._TCPSocket.__del__()

			if hasattr(self, '_UDPSocket'):
				if self._UDPSocket is not None:
					self._UDPSocket.close()

			raise RuntimeError("ERROR: Connection to the detector not available. Check network and cable settings.")


	def __del__(self):
		"""Class destructor. The following steps are performed:

		- Close the TCP socket.
		- Close the UDP socket.
		
		"""

		# Ensure to stop the polling thread:
		self._poll = False

		# Close connections to the detector:
		if hasattr(self, '_TCPSocket'):
			if self._TCPSocket is not None:
				self._TCPSocket.__del__()

		if hasattr(self, '_UDPSocket'):
			if self._UDPSocket is not None:
				self._UDPSocket.close()

		# Close the server process:
		if self._server is not None:
			subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self._server.pid))
			self._server.__del__()
			

	
	def _polling(self):
		"""
		"""
		
		# Maybe a first "wake-up" of the detector via TCP is required
		# to start the UDP broadcast.  Not clear...

		while self._poll:		
			try:		
				# Get "meteo" information via UDP:
				data, addr = self._UDPSocket.recvfrom(1024)

				# Split the data string and extract the required parameter:
				msg = data.decode(encoding='ascii', errors='ignore')
				params = msg.split("\n")

				# print(params) # FOR DEBUG

				for param in params:
					
					if param.startswith("READ_TCOLD"):
						self._tcold = float(param.split(" ")[1])
					elif param.startswith("READ_THOT"):
						self._thot = float(param.split(" ")[1])
					elif param.startswith("READ_HV"):
						self._hv = float(param.split(" ")[1])
					elif param.startswith("READ_HV_CURRENT"):
						self._hv_current = float(param.split(" ")[1])
					elif param.startswith("READ_BOX_HUM"):
						self._box_hum = float(param.split(" ")[1])
					elif param.startswith("READ_BOX_TEMP"):
						self._box_temp = float(param.split(" ")[1])
					elif param.startswith("READ_PELTIER_PWR"):
						self._peltier_pwr = float(param.split(" ")[1])

				if self._init_done:
					# If this condition holds, the detector is supposed to be operating
					# under safety conditions, i.e.  humidity below threshold and Peltier
					# temperature above safety ON temperature.  It may however happen that
					# e.g.  the nitrogen flux is having problems and therefore the humidity
					# value goes above safety threshold.  If this happens the detector
					# terminates its activity (which means stopping to thermalize).
					if (self._box_hum > self._humidity_threshold):
						print("WARNING: Humidity safety conditions do not hold anymore. Detector needs re-initialization.")

						# De-thermalize:
						self.send_command("! Env_Config -40 Off 400 Off")

						# Initialization needs to be re-done:
						self._init_done = False				

			except Exception as e:
				print("WARNING: Error while reading meteo information (" + str(e) + ")")
				pass



	def send_command(self, message):
		"""Send low-level command to the device.

		:param message: The device-specific command (check the manual).
		:type message: string

		:return: Device-response.
		:rtype: string
		
		.. note:: 

		   Normally ``send_command()`` is seldom used by a calling program since the 
		   caller is required to have a knowledge of the device-specific way to 
		   format commands. The method is anyway available for advanced user.

		"""			

		# Send the command to Pixirad:
		self._TCPSocket.send(message)

		# Receive the response from the command:
		msg = self._TCPSocket.recv_string()		

		# Recovery binary data:
		if message.startswith("! Acquire"):	

			# Reset low and high images:
			self._low = numpy.array([], dtype=numpy.uint16)
			self._high = numpy.array([], dtype=numpy.uint16)	

			if self._col == "2COL":
				repetitions = self._shots * 2
			else:
				repetitions = self._shots

			# Repeat the following instructions:
			for i in range(repetitions):
								

				# Set an array of zeros:
				npdata = numpy.zeros((self._width, self._height),dtype='<u2')

				# Get the image data:
				msg, out = self._TCPSocket.recv_image()
				
				print(msg) # FOR DEBUG...
			
				if out is not None:
					# Convert to numpy array:
					npdata = numpy.frombuffer(out, dtype='<u2')
					npdata = numpy.reshape(npdata, (self._width, self._height))
					npdata = npdata[:,::-1].T
				else:
					# Blank image:
					print("WARNING: Blank frame.")
					npdata = npdata.T

				if msg is not None:
					# Check if the image is 1COL0 or 1COL1:
					params = msg.split(" ")
					param = next((x for x in params if "DATAREG" in x))
					reg = param.split("=")[1]
					reg = int(reg)

					# For a future "live" monitor, here get a mutex ??:

					# Add to the third dimension if it is not the first image:
					if (reg == 0):
						self.image[:,:,0] = npdata
						self._low = numpy.dstack((self._low, npdata)) if self._low.size else npdata			
					else:
						# Reg == 1:
						self.image[:,:,1] = npdata
						self._high = numpy.dstack((self._high, npdata)) if self._high.size else npdata

					# For a future "live" monitor, here relase a mutex ??:

				else:
					raise Exception("ERROR: Unable to read image data. Acquisition aborted.") 				
				

		# Return the output string message (not the binary data):
		return msg
	
			
			
		


	def initialize(self, thermalize=True, calibrate=True):
		"""Perform all initialization operations.

		:param thermalize: switch on thermalization (default=True).
		:type thermalize: bool

		:param calibrate: perform auto-calibration (default=True).
		:type calibrate: bool
		
		These operations assume the detector is correctly connected to a chiller
		and it is receiving a proper flux of dry air or nitrogen. The performed 
		operations are (in order):

		- Start the "meteo" polling thread
		- Basic technical initalizations (only very first time)
		- Check and wait until BOX_HUM is below a safe ON threshold (<0.8%)
		- Start Peltier cooler (if not already ON) with an unreachable goal (i.e. -40 °C)
		- Chech and wait until TCOLD is below a safe ON threshold (e.g. -18 °C)
		- Perform autocalibration.

		After having invoked ``initialize()`` the caller is allowed to 
		acquire images by invoking ``acquire()``. An exception is raised
		if ``acquire()`` is invoked without a previous call to ``initialize()``.

		.. note::		
		   Normally these operations assume X-ray beam OFF. At the end of 
		   ``initialize()`` it should be safe to switch X-ray beam ON.

		.. note::		
		   ``initialize()`` can be called more than once to e.g. re-calibrate
		   the detector (see the note about changing MODE parameter).
		
		"""			
			

		if not self._poll:
			# Start the polling thread for "meteo" information:
			self._poll = True
			t = threading.Thread(target=self._polling)		
			t.start()

			# Wait at first for the polling thread to update the information:
			time.sleep(3)

		# Basic technical initializations:
		if not self._init_done:
			
			self._firmware = self.send_command("SYS:? GET_FIRMWARE_VERSION\n")
			self._info = self.send_command("SYS:? GET_ADDITIONAL_INFO\n")

			self.send_command("! Sensor_model_config PIII CDTE PX2")
			self.send_command("! SET_FILE_SAVING_STYLE SAVE_PX1_OLD_STYLE")
			self.send_command("! PROCESSING_FILT_CONFIG 4 4")
			self.send_command("! PROCESSING_CONFIG DEFAULT")
	
			self.send_command("! ADVANCED_MODE DISABLED")

		# Following lines need to be sent in case of restart:
		self.send_command("! SET_CROP 0 " + str(self._width - 1) + " 0 " + str(self._height - 1))
		self.send_command("! Sensor_config 28.0 28.0 " + str(self._E1) + " " + str(self._E0) + " " + str(self._vt_hit) + " " + self._col + " " + self._mode + " 100")	

		self.send_command("! Bias_Management_Config " + self._bias_mode + " " + str(self._bias_TOnDelay) + " " + str(self._bias_TOffDelay) + " " + str(self._bias_HVCycle))	
		self.send_command("DAQ:! SET_PIII_CONF 0 7 0 7 0 0")	
		
		# The following two commands are sent at any acquire in Bellazzini's
		# software:
		self.send_command("! Run_Config Data - -")
		self.send_command("! Data_Transfer_Config 1")

		# Start termalization:
		if thermalize:	

			# Wait for proper humidity:
			while (self._box_hum > self._humidity_threshold):
				print('humidity = ', self._box_hum, '%')
				time.sleep(3)
			
			# Send thermalization command:
			self.send_command("! Env_Config -40 On 400 Off")

			# Wait for proper temperature:
			while (self._tcold > self._temp_ON_threshold):
				print('T Cold = ', self._tcold, ' C')
				time.sleep(3)	
		
		# Calibrate:
		if calibrate:
			self.send_command("! Autocalibrate")
			time.sleep(5)

		
		# Set initialization done:
		self._init_done = True


	def terminate(self, dethermalize=True):
		"""Perform once-for-all closing operations.

		:param dethermalize: switch off thermalization (default=True).
		:type dethermalize: bool


		These operations are (in order):

		- Switch off thermalization
		- Wait for TCOLD to reach a safe OFF threshold (i.e. above 10 °C)
		- Stop the "meteo" polling thread

		After invoking ``terminate()``, a new call to ``initialize()`` is required  
		prior to a new acquisition. Sockets to the detector server are not 
		closed. Class destructor is responsible for closing the sockets.

		An exception is raised if ``terminate()`` is invoked without a previous 
		call to ``initialize()``.

		"""

		if self._init_done:

			# Terminate thermalization:
			if dethermalize:
				self.send_command("! Env_Config -40 Off 400 Off")

				# Wait for proper OFF temperature:
				while (self._tcold < self._temp_OFF_threshold):
					print('T Cold = ', self._tcold, ' C')
					time.sleep(3)

			# Stop the polling thread:
			self._poll = False

			# Wait for the polling thread to close:
			time.sleep(3)

			# Initialization needs to be re-done:
			self._init_done = False

		else:
			raise Exception("ERROR: Detector needs to be initialized by invoking initialize() method.") 


	def set_param(self, key, value):
		"""Set detector specific acquisition parameters.

        :param key: The device-specific parameter (see next table).
        :type key: string

        :param value: The value for the specified parameter (see next table).
        :type value: string or numerical
        

        Acquisiton read/write parameters:

        .. list-table:: 
           :widths: 30 70
           :header-rows: 1

           * - Parameter
             - Description
           * - MODE
             - { NONPI | NPI | NPISUM } (Default = NPISUM)
           * - COL
             - { DTF | 1COL0 | 1COL1 | 2COL } (Default = 2COL)
           * - E0_KEV
             - [keV] (Default = 5.0)
           * - E1_KEV
             - [keV] (Default = 60.0)
           * - VT_HIT_KEV
             - [keV] (Default = 4.0)
           * - SHOTS
             - (Default = 1)
           * - EXP_TIME_MILLISEC	    
             - [ms] (Default = 100)
           * - EXP_DELAY_MILLISEC	
             - [ms] (Default = 0)
           * - TRIGGER			    
             - { INT | EXT1 | EXT2 } (Default = INT)
           * - BIAS_MODE			    
             - { AUTOHV | AUTOHV_LC | AUTOHV_LC | STDHV } (Default = AUTOHV)
           * - BIAS_TONDELAY_SEC	    
             - [s] (Default = 1.0)
           * - BIAS_TOFFDELAY_SEC
             - [s] (Default = 4.0)
           * - BIAS_HVCYCLE
             - (Default = 5)
        
        
        An exception is raised if an invalid parameter is passed as input.

        .. Warning::
           A change of MODE requires detector re-calibration and re-calibration needs to 
           be performed with X-ray beam off. Since this code does not perform
           assumptions for the X-ray status, an automatic recalibration is not performed.
           The caller should perform re-calibration by e.g. calling again ``initialize()``.
           Here is an example of how to perform a proper change of MODE: ::

               src.off() # X-rays off

               det.set_param("MODE", "NONPI")
               det.initialize()

               src.on()  # X-rays on

           
           A second call to ``initalize()`` can be performed even if ``terminate()`` has 
           not been invoked between first and second call.

        """

		if key in ["MODE", "COL", "E0_KEV", "E1_KEV", "VT_HIT_KEV"]:
			
			if key == "MODE":
				self._mode = value # Change of "MODE" however requires re-calibration
			elif key == "COL":
				self._col = value
			elif key == "E0_KEV":
				self._E0 = float(value)
			elif key == "E1_KEV":
				self._E1 = float(value)
			elif key == "VT_HIT_KEV":
				self._vt_hit = float(value)

			# Send the command:
			self.send_command("! Sensor_config 28.0 28.0 " + str(self._E1) + " " + str(self._E0) + " " + str(self._vt_hit) + " " + self._col + " " + self._mode + " 2000")	
		
		elif key in ["BIAS_MODE", "BIAS_TONDELAY_SEC", "BIAS_TOFFDELAY_SEC", "BIAS_HVCYCLE"]:

			if key == "BIAS_MODE":
				self._bias_mode = value
			elif key == "BIAS_TONDELAY_SEC":
				self._bias_TOnDelay = float(value)
			elif key == "BIAS_TOFFDELAY_SEC":
				self._bias_TOffDelay = float(value)
			elif key == "BIAS_HVCYCLE":
				self._bias_HVCycle = int(value)

			# Send the command:
			self.send_command("! Bias_Management_Config " + self._bias_mode + " " + str(self._bias_TOnDelay) + " " + str(self._bias_TOffDelay) + " " + str(self._bias_HVCycle))		

		elif key in ["SHOTS", "EXP_TIME_MILLISEC", "EXP_DELAY_MILLISEC", "TRIGGER"]:

			if key == "SHOTS":
				self._shots = int(value)
			elif key == "EXP_TIME_MILLISEC":
				self._exp_time = int(value)
				# Change also TCP time_out:
				self._TCPSocket.settimeout(max(20,int((self._exp_time/1000)*2)))
			elif key == "EXP_DELAY_MILLISEC":
				self._exp_delay = int(value)
			elif key == "TRIGGER":
				self._trigger = value

			# No need to send a command.  They are part of an acquire() call.
		
		else:
			raise Exception("ERROR: Parameter " + str(key) + " is invalid.")


	def get_param(self, key):
		"""Get detector specific acquisition as well as status parameters.
		
		:param key: The device-specific parameter (see next table).
		:type key: string

		:return: The value for the specified parameter.
		:rtype: string or numerical


        Acquisiton read/write parameters:

        .. list-table:: 
           :widths: 30 70
           :header-rows: 1

           * - Parameter
             - Description
           * - MODE
             - { NONPI | NPI | NPISUM } (Default = NPISUM)
           * - COL
             - { DTF | 1COL0 | 1COL1 | 2COL } (Default = 2COL)
           * - E0_KEV
             - [keV] (Default = 5.0)
           * - E1_KEV
             - [keV] (Default = 60.0)
           * - VT_HIT_KEV
             - [keV] (Default = 4.0)
           * - SHOTS
             - (Default = 1)
           * - EXP_TIME_MILLISEC	    
             - [ms] (Default = 100)
           * - EXP_DELAY_MILLISEC	
             - [ms] (Default = 0)
           * - TRIGGER			    
             - { INT | EXT1 | EXT2 } (Default = INT)
           * - BIAS_MODE			    
             - { AUTOHV | AUTOHV_LC | AUTOHV_LC | STDHV } (Default = AUTOHV)
           * - BIAS_TONDELAY_SEC	    
             - [s] (Default = 1.0)
           * - BIAS_TOFFDELAY_SEC
             - [s] (Default = 4.0)
           * - BIAS_HVCYCLE
             - (Default = 5)
                    

        .. list-table:: 
           :widths: 100
           :header-rows: 1

           * - Status parameter
           * - TCOLD       [°C]
           * - THOT        [°C]
           * - HV          [V]
           * - HV_CURRENT  [nA]
           * - BOX_HUM	  [%]
           * - BOX_TEMP    [°C] 
           * - PELTIER_PWR [%]
        
        An exception is raised if an invalid parameter is passed as input.

		"""
		
		
		if key == "MODE":
			value = self._mode 
		elif key == "COL":
			value = self._col
		elif key == "E0_KEV":
			value = self._E0
		elif key == "E1_KEV":
			value = self._E1
		elif key == "VT_HIT_KEV":
			value = self._vt_hit

		elif key == "BIAS_MODE":
			value = self._bias_mode
		elif key == "BIAS_TONDELAY_SEC":
			value = self._bias_TOnDelay
		elif key == "BIAS_TOFFDELAY_SEC":
			value = self._bias_TOffDelay
		elif key == "BIAS_HVCYCLE":
			value = self._bias_HVCycle

		elif key == "SHOTS":
			value = self._shots
		elif key == "EXP_TIME_MILLISEC":
			value = self._exp_time
		elif key == "EXP_DELAY_MILLISEC":
			value = self._exp_delay
		elif key == "TRIGGER":
			value = self._trigger


		elif key == "TCOLD":
			value = self._tcold # Change of modality however should require re-calibration
		elif key == "THOT":
			value = self._thot
		elif key == "HV":
			value = self._hv
		elif key == "HV_CURRENT":
			value = self._hv_current
		elif key == "BOX_HUM":
			value = self._box_hum
		elif key == "BOX_TEMP":
			value = self._box_temp
		elif key == "PELTIER_PWR":
			value = self._peltier_pwr

		else:
			raise Exception("ERROR: Parameter " + str(key) + " is invalid.")
		
		return value		




	def acquire(self, max_attempts=5):
		""" Acquire one or more images according to the specified settings. 

		:param max_attempts: this method automatically repeat the command
			for the specified amount of attempts if errors occur (default = 5).
		:type max_attempts: numerical

		:return: the acquired image(s).
		:rtype: numpy array(s)

		An exception is raised if ``acquire()`` is invoked without a previous 
		call to ``initialize()``.
		
		.. note ::
		   The default version of ``acquire`` is blocking therefore an estimated
		   overhead of about 1.2 s needs to be considered for each acquisition.
		   The total execution time of the default version of ``acquire`` is
		   therefore t = shots * exp_time + ~1.2 s, independently of the 
		   acquisition modality (1COL or 2COL).
		   If there is the need to gain this ~1.2 s overhead time a non-blocking
		   version of ``acquire`` needs to be designed.
				

		"""

		if self._init_done:

			attempts_ct = 0

			while (attempts_ct < max_attempts):

				try:

					# Six commands are sent to the server for each acquisition in Bellazzini's software:
					#self.send_command("! Sensor_config 28.0 28.0 " + str(self._E1) + " " + str(self._E0) + " " + str(self._vt_hit) + " " + self._col + " " + self._mode + " 2000")
					#self.send_command("! Bias_Management_Config " + self._bias_mode + " " + str(self._bias_TOnDelay) + " " + str(self._bias_TOffDelay) + " " + str(self._bias_HVCycle))
					#self.send_command("! Run_Config Data test.dat -")			
					#self.send_command("! Data_Transfer_Config 1")

					# Run the actual acquisition command:
					self.send_command("! Acquire " + str(self._shots) + " " + str(self._exp_time) + " " + str(self._exp_delay) + " " + self._col + " " + self._trigger + " " + self._bias_mode)
			
					# Return the image(s) as numpy array:
					return self._low, self._high			

				except Exception as e:

					# Increment counter:
					attempts_ct = attempts_ct + 1

					print("WARNING: Acquisition error(s). Restarting the TCP communication...")
			
					# Restart the server process:						
					self._TCPSocket.__del__()

					# On Windows only:
					subprocess.Popen("TASKKILL /F /PID {pid} /T".format(pid=self._server.pid))
					self._server.__del__()
					time.sleep(1)

					self._server = subprocess.Popen(self._srv_path, creationflags=subprocess.CREATE_NEW_CONSOLE)
					time.sleep(1)

					self._TCPSocket.restart()
					time.sleep(1)
			
					print("WARNING: Socket restarted. Now re-initializing...")

					self._init_done = False
					# It would be actually a good change to recalibrate but a shutter is needed:
					self.initialize(thermalize=True, calibrate=False)
					print("WARNING: Detector re-initialized.")		
					
			# Following line is reached when maximum number of attempts is reached:
			raise Exception("ERROR: Cannot communicate with the detector. Software stops.") 

		else:
			raise Exception("ERROR: Detector needs to be initialized by invoking initialize() method.") 



	def serialize(self):
		"""Serialize object status by returning a dictionary, i.e. parameters in key:value pairs.
		
		:return: Object status. 
		:rtype: dictionary

		"""
		
		# Creating a dictionary:
		dict = {
				"Detector": "Pixirad-1 | Pixie-III",				

				"BOX_HUM": self._box_hum,
				"TCOLD":self._tcold,
				"PELTIER_PWR": self._peltier_pwr,
				"THOT": self._thot,
				"HV": self._hv,
				"HV_CURRENT": self._hv_current,				
				"BOX_TEMP": self._box_temp,				

				"MODE": self._mode,
				"COL": self._col,
				"E0_KEV": self._E0,
				"E1_KEV": self._E1,
				"VT_HIT_KEV": self._vt_hit,

				"SHOTS": self._shots,
				"EXP_TIME_MILLISEC": self._exp_time,
				"EXP_DELAY_MILLISEC": self._exp_delay,
				"TRIGGER": self._trigger,

				"BIAS_MODE": self._bias_mode,
				"BIAS_TONDELAY_SEC": self._bias_TOnDelay,
				"BIAS_TOFFDELAY_SEC": self._bias_TOffDelay,
				"BIAS_HVCYCLE": self._bias_HVCycle,

				"FIRMWARE":	self._firmware
				}

		return dict