

from MikesServoMapper import MikesServoMapper


import argparse


def main():
	
	parser = argparse.ArgumentParser(
		prog="Mike's Servo Mapper (for adafruit driver board)"
	)
	parser.add_argument(
		"--config", "--config-file",
		help="Path to a yaml file describing some configuration stuffs",
		required=False,
		default=None,
		dest="config_file"
	)
	parser.add_argument(
		"--name",
		help="Specify a target name (can be used multiple times)",
		required=False,
		default=[],
		action="append",
		dest="names"
	)
	
	args = parser.parse_args()
	
	mapper = MikesServoMapper(
		config_file=args.config_file,
		names=args.names
	)
	mapper.run()


if __name__ == "__main__":
	main()

