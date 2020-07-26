

import logging
import pprint
import sys
import yaml


class MikesServoMapper:
	
	def __init__(self, config_file: str, names):
		
		# noinspection PyTypeChecker
		self.__logger: logging.Logger = None
		self.__logger_formatter = None
		self.init_logging()
		
		self.__names = list(names)
		self.__names.sort()
		
		self.__config = None
		self.load_config(config_file)
		self.pull_config_names()
		
		self.__logger.info("Names: %s" % (pprint.pformat(self.__names)))
	
	def init_logging(self):
		
		self.__logger = logging.Logger("Mikes Servo Mapper")
		self.__logger_formatter = logging.Formatter(fmt="Hi poop")
		
		stream_handler = logging.StreamHandler(sys.stdout)
		
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

