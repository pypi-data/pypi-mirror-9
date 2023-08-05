import os
from setuptools import setup, find_packages
version = '0.1.1'
README = os.path.join(os.path.dirname(__file__), 'README.md')
long_description = open(README).read() + '\n'
setup(name='sdfpy',
      version=version,
      description=("Self-Describing File Reader"),
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
          ("Topic :: Software Development :: Libraries :: Python Modules"),
      ],
      keywords='data',
      url="http://bitbucket.org/darkskysims/sdfpy",
      author='Samuel Skillman <samskillman@gmail.com>, Matthew Turk <matthewturk@gmail.com>, Michael S. Warren <mswarren@gmail.com>',
      license='BSD',
      packages=find_packages(),
      install_requires = ['thingking'],
      )
