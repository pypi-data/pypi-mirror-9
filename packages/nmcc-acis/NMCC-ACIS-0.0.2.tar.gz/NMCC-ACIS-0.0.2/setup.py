# Standard Library Imports
import os
from setuptools import setup


# Allow setup.py to be run from any path.
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


setup(
    name = 'NMCC-ACIS', 
    version = '0.0.2', 
    url = 'https://bitbucket.org/nmclimate/nmcc-acis/', 
    author = 'Stanley Engle', 
    author_email = 'sengle@nmsu.edu', 
    description = 'A package that retrieves and formats ACIS data.', 
    license = 'BSD', 
    packages = ['nmccacis', 
    	'nmccacis.stndata'], 
    include_package_data = True,
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', 
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)


