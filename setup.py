from distutils.core import setup
from os.path import join, dirname

import setuptools

import mrb

with open(join(dirname(__file__), 'requirements.txt'), 'r') as f:
    install_requires = f.read().split("\n")

setup(name='mqtt-rest-bridge',
      version=mrb.__version__,
      author=mrb.__author__,
      install_requires=install_requires,
      description=mrb.__doc__.strip(),
      python_requires='>=3.6',
      packages=setuptools.find_packages(),
      )
