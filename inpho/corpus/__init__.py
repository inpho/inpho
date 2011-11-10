from datetime import datetime
import logging
import os

import inpho

# get corpus path
path = inpho.config.get('corpus', 'path')

# set up data paths
occur_path = inpho.config.get_data_path('occur', 'corpus')
fuzzy_path = inpho.config.get_data_path('fuzzy', 'corpus')
sql_path = inpho.config.get_data_path('sql', 'corpus')

# set up logging
log = logging.getLogger('mining')
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
log.addHandler(file_handler)
