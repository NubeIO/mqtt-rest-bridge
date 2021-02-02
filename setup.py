from distutils.core import setup

import setuptools

import mrb

requirements = [
    'paho-mqtt==1.5.1',
]

setup(name='mqtt-rest-bridge',
      version=mrb.__version__,
      author=mrb.__author__,
      install_requires=requirements,
      description=mrb.__doc__.strip(),
      python_requires='>=3.6',
      packages=setuptools.find_packages(),
      )
