'''
Imports configuration files for use with the inpho libraries.
'''
import os.path
import logging
config_paths = [os.path.abspath("inpho.ini"), 
                os.path.expanduser("~/.config/inpho/inpho.ini")]

config_path = None
for path in config_paths:
    if os.path.exists(path):
        config_path = path
        break

logging.debug("Using config path: %s" % config_path)

# Configuration file does not exist, raise Exception
if config_path is None:
    raise IOError("Missing inpho.ini configuration file.")

from ConfigParser import ConfigParser
config = ConfigParser()
config.read(config_path)

