#!/usr/bin/env python

import bdist_debian
from distutils.core import setup

setup(
    name='ienabler',
    scripts=['ienabler-cmd.py', 'ienabler-gui.py'],
    py_modules=['ienabler'],
    version='1.0',
    maintainer='John Stowers',
    maintainer_email='john.stowers@gmail.com',
    depends='python2.5',
    license="BSD",
    section="user/other",
    architecture="all",
    essential="no",
    description="Univeristy of Canterbury IEnabler",
    data_files=[
        ('share/applications', ['ienabler.desktop']),
        ('share/pixmaps', ['uclogo.svg'])],
    cmdclass={
        'bdist_debian': bdist_debian.bdist_debian}
)



