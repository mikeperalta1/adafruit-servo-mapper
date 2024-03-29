

from adafruit_servokit import ServoKit


import getch
import logging
import os
import pprint
import sys
import time
import yaml


class MikesServoMapper:
	
	__BASE_I2C_ADDRESS = 0x40
	__CHANNELS_COUNT = 16
	
	__DEFAULT_SERVO_DEGREES = 180
	__DEFAULT_JIGGLE_DURATION = 2
	__DEFAULT_JIGGLE_SLICES = 50
	
	__ESCAPE_KEY = chr(27)
	
	__DEFAULT_OUTPUT_FILE_NAME = "servo-mappings.yml"
	__DEFAULT_SERVO_CHANNEL_MAPPING_KEY = "servo-to-channel"
	
	def __init__(self, config_file: str = None, names=None, output_file: str = None):
		
		# noinspection PyTypeChecker
		self.__logger: logging.Logger = None
		self.__logger_formatter = None
		self.init_logging()
		
		if names is None:
			self.__names = list()
		else:
			self.__names = list(names)
		self.__names.sort()
		
		self.__config = None
		self.load_config(config_file)
		self.pull_config_names()
		self.__logger.info("Names: %s" % (pprint.pformat(self.__names)))
		
		self.__output_file_path = output_file
		if self.__output_file_path is None:
			self.__output_file_path = self.make_default_mappings_output_file_path()
		
		self.__mappings = {}
	
	def init_logging(self):
		
		self.__logger = logging.Logger("Mikes Servo Mapper")
		self.__logger_formatter = logging.Formatter(fmt="[%(asctime)s][%(name)s] %(message)s")
		
		stream_handler = logging.StreamHandler(sys.stdout)
		stream_handler.setFormatter(self.__logger_formatter)
		
		self.__logger.addHandler(stream_handler)
		
		self.__logger.info("Logging initialized")
	
	def load_config(self, config_file):
		
		if config_file is None:
			return
		
		with open(config_file) as f:
			
			config = yaml.safe_load(f)
		
		self.__logger.info("Loaded config: %s" % (pprint.pformat(config),))
		
		self.__config = config
	
	def pull_config_names(self):
		
		if self.__config is None:
			self.__logger.info("No config specified; Won't pull names")
			return
		self.__logger.info("Pulling names from config")
		
		if "names" not in self.__config:
			self.__logger.warning("Key \"names\" is not in config; Cannot pull names")
			return
			
		config_names = self.__config["names"]
		if not isinstance(config_names, list):
			self.__logger.warning("Config had key \"names\" but it wasn't a list; Won't pull names")
			return
		
		self.__logger.info("Names before pulling from config: %s" % (self.__names,))
		for name in config_names:
			self.__names.append(name)
		self.__names.sort()
		self.__logger.info("Names after pulling from config: %s" % (self.__names,))
	
	def set_name_mapping(self, name, channel):
		
		self.__mappings[name] = channel
	
	def get_name_mapping(self, name):
		
		if name in self.__mappings:
			return self.__mappings[name]
		
		return None
	
	def determine_i2c_address(self):
		
		return self.__BASE_I2C_ADDRESS
	
	def run(self):
		
		self.__logger.info("Running!")
		
		while True:
			
			self.__logger.info("")
			self.__logger.info("Please choose a mode: ")
			self.__logger.info("1. Edit mappings")
			self.__logger.info("2. Test current mappings")
			self.__logger.info("3. Write mappings to file")
			self.__logger.info("4. Load previously saved mappings")
			self.__logger.info("Q. Quit")
			user_choice = getch.getch()
			
			if user_choice == "q" or user_choice == "Q":
				self.__logger.info("Quitting!")
				break
			
			if user_choice == "1":
				self.edit_mappings()
			elif user_choice == "2":
				self.test_mappings()
			elif user_choice == "3":
				self.write_mappings()
			elif user_choice == "4":
				self.load_mappings()
			else:
				self.__logger.warning("Invalid choice: %s" % user_choice)
	
	def get_servo_kit(self):
		
		i2c_address = self.determine_i2c_address()
		servo_kit = ServoKit(
			address=i2c_address,
			channels=self.__CHANNELS_COUNT
		)
		
		return servo_kit
	
	def edit_mappings(self):
		
		self.__logger.info("Begin mapping mode !")
		
		#
		servo_kit = self.get_servo_kit()
		
		#
		while True:
			
			# Print all current mappings
			self.__logger.info("")
			self.__logger.info("Current Mappings:")
			menu_number_to_name = {}
			for name_index in range(len(self.__names)):
				
				name = self.__names[name_index]
				name_number = name_index + 1
				menu_number_to_name[str(name_number)] = name
				
				self.__logger.info(
					"%s. %s ==> %s"
					% (name_number, name, self.get_name_mapping(name=name))
				)
			
			self.__logger.info("")
			self.__logger.info("Please enter a number to change the corresponding mapping, or Q to quit.")
			user_input = input()
			if user_input == "Q" or user_input == "q":
				self.__logger.info("Quitting mapping mode")
				break
			elif user_input in menu_number_to_name:
				name = menu_number_to_name[user_input]
				channel = self.run_one_mapping(
					servo_kit=servo_kit,
					name=name,
					default_channel=self.get_name_mapping(name)
				)
				self.set_name_mapping(name=name, channel=channel)
			else:
				self.__logger.warning("Invalid input: %s" % user_input)
	
	def run_one_mapping(self, servo_kit, name, default_channel=None):
		
		selected_channel = default_channel
		
		while True:
			
			self.__logger.info("")
			self.__logger.info("Mapping channel for: %s" % (name,))
			self.__logger.info(
				"Press a key between 0-9 and A-F to try a channel."
			)
			self.__logger.info(
				"Press the space bar when you've found the correct channel, or escape to abort."
			)
			self.__logger.info("Currently selected channel: %s" % selected_channel)
			
			key = getch.getch().lower()
			if key == self.__ESCAPE_KEY:
				self.__logger.info("Aborting")
				selected_channel = None
				break
			elif key == " ":
				self.__logger.info("Selected channel: %s" % selected_channel)
				break
			else:
				
				try:
					channel = int(key, 16)
					selected_channel = channel
					self.jiggle_channel(servo_kit=servo_kit, channel=channel)
				except ValueError:
					self.__logger.warning("Invalid input!: %s" % (key,))
					time.sleep(1)
		
		return selected_channel
	
	def test_mappings(self):
	
		self.__logger.info("Testing mappings!")
		
		#
		servo_kit = self.get_servo_kit()
		
		#
		for name in self.__mappings.keys():
			
			channel = self.get_name_mapping(name=name)
			self.__logger.info("Jiggling mapping: %s ==> %s" % (name, channel))
			self.jiggle_channel(servo_kit=servo_kit, channel=channel)
		
		self.__logger.info("Done testing mappings")
	
	def jiggle_channel(self, servo_kit, channel):
		
		duration = self.__DEFAULT_JIGGLE_DURATION
		
		degrees_per_slice = self.__DEFAULT_SERVO_DEGREES / self.__DEFAULT_JIGGLE_SLICES
		seconds_per_slice = duration / self.__DEFAULT_JIGGLE_SLICES
		
		self.__logger.info(
			"Jiggling servo on channel #%s using %s slices over %s seconds"
			% (channel, self.__DEFAULT_JIGGLE_SLICES, duration)
		)
		
		servo = servo_kit.servo[channel]
		
		# Jiggle
		for slice_index in range(self.__DEFAULT_JIGGLE_SLICES):
			
			angle = 0 + (degrees_per_slice * slice_index)
			servo.angle = angle
			time.sleep(seconds_per_slice)
		
		# Center
		servo.angle = 90
	
	def make_default_mappings_output_file_path(self):
		
		output_file_path = os.path.join(
			"output",
			self.__DEFAULT_OUTPUT_FILE_NAME
		)
		
		return output_file_path
	
	def write_mappings(self):
		
		output_file_path = self.__output_file_path
		
		self.__logger.info("Writing mappings to output file: %s" % (output_file_path,))
		
		data = {
			self.__DEFAULT_SERVO_CHANNEL_MAPPING_KEY: self.__mappings
		}
		
		with open(output_file_path, 'w') as f:
			yaml.dump(data, f, default_flow_style=False)
	
	def load_mappings(self, file_path=None):
		
		if file_path is None:
			file_path = self.__output_file_path
		
		self.__logger.info("Attempting to load mappings from: %s" % (file_path,))
		
		with open(file_path) as f:
			loaded_data = yaml.safe_load(f)
		
		if self.__DEFAULT_SERVO_CHANNEL_MAPPING_KEY not in loaded_data.keys():
			self.__logger.warning("Could not find key 'servo-mappings' in loaded data")
			return
		
		mappings = loaded_data[self.__DEFAULT_SERVO_CHANNEL_MAPPING_KEY]
		if not isinstance(mappings, dict):
			self.__logger.warning("Mappings aren't in dict format; Won't load")
			return
		
		for name in mappings.keys():
			
			self.__logger.info("Examining mapping: %s" % (name,))
			
			channel = mappings[name]
			
			if not isinstance(channel, int):
				self.__logger.warning("Mapping isn't an integer; Ignoring: %s" % channel)
				continue
			
			self.__logger.info("Loading mapping: %s ==> %s" % (name, channel))
			self.set_name_mapping(name=name, channel=channel)
		
		self.__logger.info("Done loading mappings")
