from distutils.core import setup
import os
from pycse import __version__

setup(name = 'pycse',
      version=__version__,
      description='python computations in science and engineering',
      url='http://github.com/jkitchin/pycse',
      maintainer='John Kitchin',
      maintainer_email='jkitchin@andrew.cmu.edu',
      license='GPL',
      platforms=['linux'],
      packages=['pycse'],
      scripts=['pycse/publish.py'],
      install_requires=['quantities'],
      data_files=['requirements.txt'],
      long_description='''\
python computations in science and engineering
===============================================

This package provides some utilities to perform:
1. linear and nonlinear regression with confidence intervals
2. Solve some boundary value problems.

See http://jkitchin.github.io/pycse for documentation.

      ''')

# python setup.py register to setup user
# to push to pypi - python setup.py sdist upload
