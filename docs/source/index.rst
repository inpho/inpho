====================================================
The Indiana Philosophy Ontology (InPhO) Project
====================================================

.. contents:: Table of Contents

Issue Tracking
'''''''''''''''''''
If you find errors in the InPhO, including this documentation, please file a bug
on our issue tracker at `http://inphodev.cogs.indiana.edu:8000
<http://inphodev.cogs.indiana.edu:8000>`_. Bug reports may be filed anonymously.

To request an account and join the development mailing list, please contact
`inpho@indiana.edu <mailto:inpho@indiana.edu>`_.

Requirements
''''''''''''''''''
The InPhO uses a suite of open-source software to power our dynamic ontology.
Below is a list of our open-source repositories, dependencies and data dumps.


Dependencies
-------------------
The InPhO Project depends on the following packages and utilities. Instructions
for install on Debian-based Linux Distributions and Max OS X follow.

`git <http://git-scm.com/download>`_
    version control system
`MySQL 5.5 <http://dev.mysql.com/downloads/mysql/5.5.html>`_
    database engine (InPhO is known to work with `MySQL 5.1
    <http://dev.mysql.com/downloads/mysql/5.1.html>`_, but is deployed to a
    server with 5.5. Backwards compatibility will not be guaranteed)
`Python 2.6 <http://python.org/download/releases/2.6.7/>`_
    runtime environment
`setuptools <http://pypi.python.org/pypi/setuptools>`_
    Python package manager
`virtualenv <http://pypi.python.org/pypi/virtualenv>`_
    for environment sandboxing (easier testing)
`nltk <http://www.nltk.org/download>`_
    for data mining tools
`GCC <http://gcc.gnu.org/>`_
    for compilation of `Ferenc Bodon's APRIORI frequent itemset miner
    <http://www.cs.bme.hu/~bodon/en/apriori/>`_


Debian/Ubuntu
""""""""""""""""""""
Debian-based Linux distributions (including Ubuntu) can use the following
command to install all required dependencies::

    sudo apt-get install git python2.6-dev mysql-server python-setuptools python-virtualenv python-nltk build-essential

Mac OS X
"""""""""""""""""""""
On Max OS X 10.6, GCC 4.2.1 and Python 2.6.1 are already installed, along with the setuptools
package.

To install git, see the `Help.GitHub article for OS X
<http://help.github.com/mac-set-up-git/>`_.

For the MySQL install, Tony Amoyal has `a good summary
<http://www.tonyamoyal.com/2010/04/13/install-mysql-on-mac-os-x-10-6-and-add-startupitem/>`_
of the steps required. Contact your system administrator to install and
configure this, as MySQL is a server process and additional security steps may
need to be taken.

To install virtualenv and nltk simply run::

    sudo easy_install virtualenv nltk


Data
-----------------------
The InPhO monitors a lot of data. There are three data dumps that are required:

1.  *InPhO Entity Database* – This is the seed for the InPhO database without
    users and evaluation data. It is published nightly, with monthly archives,
    corresponding to the monthly OWL file.
2.  *Stanford Encyclopedia of Philosophy* – The default corpus for the InPhO,
    used for gathering statistical information. It is published nightly, with
    quarterly archives, apt for publication.
3.  *Co-occurrence and entropy graph* – This may be computed manually for any
    entity/corpus pair by using the inpho.corpus.sep module, but nightly dumps
    are published, along with quarterly archives corresponding to the SEP and
    InPhO Entity dump present at that time.

These dumps are not yet available.

Source Code
--------------
The InPhO source is hosted on `GitHub <https://github.com/inpho>`_ in two
separate repositories:

`inpho <https://github.com/inpho/inpho>`_
    The inpho repository contains the data model and corpus-mining tools. May be
    used without the inphosite module.
`inphosite <https://github.com/inpho/inphosite>`_
    The inphosite repository contains the website, which includes the API.
    Requires the inpho module.

We encourage collaboration, and invite correspondence through
`inpho@indiana.edu <mailto:inpho@indiana.edu>`_. Feel free to fork our
repositories, and use GitHub to `submit a pull request
<http://help.github.com/send-pull-requests/>`_.



Installation
'''''''''''''''
After all dependencies are installed... [not yet complete]

1.  Configure MySQL user
#.  Import entity database
#.  Import graph
#.  Download corpus
#.  Configure inpho.ini
#.  Create virtualenv sandbox::
    
        virtualenv sandbox

#.  Activate sandbox::
        
        source sandbox/bin/activate

#.  Install inpho repository to sandbox::

        git clone git:github.com/inpho/inpho.git
        python inpho/setup.py develop

#.  Install inphosite repository to sandbox::

        git clone git:github.com/inpho/inphosite.git
        python inphosite/setup.py develop

#.  Configure development.ini

#.  Start inphosite server::

        cd inphosite
        paster serve --reload development.ini

    We reccommend using the `GNU Screen <http://www.gnu.org/s/screen/>`_ utility
    to keep a persistent server running.

Collaboration
'''''''''''''''''
We invite collaboration
Contact us at inpho@indiana.edu
