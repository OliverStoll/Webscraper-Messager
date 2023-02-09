""" Load the config file and provide access to the config values. """

import yaml


# open config file and load it
try:
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    with open('../config.yaml', 'r') as f:
        config = yaml.safe_load(f)