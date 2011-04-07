#!/bin/sh
virtualenv --no-site-packages sandbox
source sandbox/bin/activate
easy_install PyYAML
easy_install nltk
python setup.py develop
cd apriori-source
make
