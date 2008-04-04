#!/usr/bin/env python

import bdist_debian
from distutils.core import setup

setup(name='ienabler',
      scripts=['ienabler-cmd.py', 'ienabler-gui.py'],
      py_modules=['ienabler'],
      version='1.0',
      section='user/backups',
      maintainer='John Stowers',
      maintainer_email='John Stowers <john.stowers@gmail.com>',
      depends='python2.5',
      description="Wireless backup application",
      long_description="Quickly back up your data to a server over wireless.",
      data_files=[('share/applications', ['ienabler.desktop']),
                  ('share/pixmaps', ['uclogo.svg'])],
      cmdclass={'bdist_debian': bdist_debian.bdist_debian})



