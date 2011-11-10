from datetime import datetime
import logging
from multiprocessing import Queue
import os

import inpho
from inpho.lib.log import *

# get corpus path
path = inpho.config.get('corpus', 'path')

# set up data paths
occur_path = inpho.config.get_data_path('occur', 'corpus')
fuzzy_path = inpho.config.get_data_path('fuzzy', 'corpus')
sql_path = inpho.config.get_data_path('sql', 'corpus')

# set up logging
log = logging.getLogger('')
log.setLevel(logging.DEBUG)

# configure logfilename
timestamp = datetime.now().strftime('%Y%m%d-%H%M')
logfilename = os.path.join('logs', '%s.log' % timestamp) 

if not os.path.exists('logs'):
    os.mkdir('logs')

print os.path.abspath(logfilename)

# add filehandler
file_handler = logging.FileHandler(logfilename)
file_handler.setLevel(logging.DEBUG)
# add multiprocessing handler
logQueue = multiprocessing.Queue(-1)
mp_handler = MultiprocessingHandler(file_handler, logQueue)
log.addHandler(mp_handler)
