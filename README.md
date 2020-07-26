
# Mike's Servo Mapper

A simple command line utility to map servos to 

Written and tested using the Adafruit I2C servo driver board: [PCA9685](https://www.adafruit.com/product/815)

## Requiremments

### Python Requirements

Python's requirements are handled by pipenv, which you can install like so:

```bash
sudo apt install pipenv
```
or
```bash
sudo dnf install pipenv
```

Once installed, you can have pipenv install all python requirements like so:

1. cd to this repo's directory
2. Execute the command: ```pipenv install```

## Execution

cd to this repo's directory and execute using:

```pipenv run python3 main.py```

## Command Line Arguments

### ***--name*** (Specify one or more mapping names)

You can specify desired mapping names by adding the ***--name*** argument, as many times as you wish:

```bash
$ pipenv run python3 main.py --name Leg --name Arm
```

### ***--config*** (Specify an input config file)

You can specify a yaml configuration file to load with this argument, like so:

```bash
$ pipenv run python3 main.py --config /path/to/config.yaml
```

So far the config file is only good for storing desired names to be mapped. Here's an example:

```yaml

names:
    - Manny
    - Moe
    - Jack

```

