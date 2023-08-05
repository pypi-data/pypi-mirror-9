import os
from setuptools import setup


#README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
README = ''

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name = 'nmcc-acis',
    version = '0.0.1a3',
    packages = ['nmccacis', 
        'nmccacis.products', 
    	'nmccacis.products.stndata'], 
    include_package_data = True,
    license = 'BSD License', 
    description = 'A package that retrieves and formats ACIS data.',
    long_description = README,
    url = 'https://bitbucket.org/nmclimate/nmcc-acis/',
    author = 'Stanley Engle',
    author_email = 'sengle@nmsu.edu',
    classifiers = [
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License', 
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)


