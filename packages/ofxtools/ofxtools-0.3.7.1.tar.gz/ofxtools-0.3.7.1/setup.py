from setuptools import setup, find_packages
from distutils.core import setup

# Get the long description from the relevant file
with open('README', 'r') as f:
    long_description = f.read()
    
setup(
    name = 'ofxtools',
    version = '0.3.7.1',
    description = ('Library for working with Open Financial Exchange (OFX) '
                 'formatted data used by financial institutions'),
    long_description = long_description,

    url = 'https://github.com/csingley/ofxtools',
    download_url = 'https://github.com/csingley/ofxtools/tarball/0.3.7.1',

    author = 'Christopher Singley',
    author_email = 'csingley@gmail.com',

    license = 'MIT',

    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Topic :: Office/Business',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Office/Business :: Financial :: Investment',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Natural Language :: English', 
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],

    keywords = ['ofx', 'Open Financial Exchange'],

    packages = find_packages(),

    extras_require = {
        'SQL': ['sqlalchemy > 0.9.8',],
    },

    package_data = {
        'ofxtools': ['config/*.cfg', 'tests/*'],
    },

    entry_points = {
        'console_scripts': [
            'ofxget=ofxtools.Client:main',
        ],
    },
)

