from distutils.core import setup

import mrb

setup(name='mqtt-rest-bridge',
      version=mrb.__version__,
      author=mrb.__author__,
      description=mrb.__doc__.strip(),
      packages=['mrb']
      )
