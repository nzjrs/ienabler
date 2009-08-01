#!/usr/bin/env python

from distutils.core import setup

setup(
    name="ienabler",
    version="1.0",
    description="Univeristy of Canterbury IEnabler",
    author="John Stowers",
    author_email="john.stowers@gmail.com",
    url="http://nzjrs.github.com/ienabler ",
    license="GPL v2",
    scripts=["ienabler-cmd.py", "ienabler-gui.py"],
    py_modules=["ienabler"],
    data_files=[
        ('share/applications', ['ienabler.desktop']),
        ('share/pixmaps', ['uclogo.svg'])],
)



