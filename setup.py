# chardet's setup.py
from distutils.core import setup
import setuptools
setup(
    name = "inpho",
    packages = ["inpho", "inpho.model"],
    version = "0.1",
    description = "Indiana Philosophy Ontology Project data processing tools",
    author = "The Indiana Philosophy Ontology (InPhO) Project",
    author_email = "inpho@indiana.edu",
    url = "http://inpho.cogs.indiana.edu/",
    download_url = "http://www.github.com/inpho/inpho",
    keywords = ["taxonomy", "ontology"],
    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
        "Topic :: Text Processing :: Linguistic",
        ],
    install_requires=[
        "mysql-python>=1.2",
        "SQLAlchemy>=0.6.0,<=0.6.99",
        "inflect>=0.2.0,<=0.2.99",
        "BeautifulSoup>=3.2.0,<=3.2.99"
    ],

    long_description = """\
Indiana Philosophy Ontology (InPhO) Project
----------------------------------------------------------

Contains scriptable libraries for using the Indiana Philosophy Ontology (InPhO).

"""
)
