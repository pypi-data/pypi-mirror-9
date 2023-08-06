#! /usr/bin/python

from setuptools.command import easy_install
from setuptools import setup, find_packages
import shutil
import os.path
import sys
import hashlib

PKG_DIR = os.path.abspath(os.path.dirname(__file__))
PKG_NAME = os.path.basename(PKG_DIR)

# Make it possible to overide script wrapping
old_is_python_script = easy_install.is_python_script
def is_python_script(script_text, filename):
    if 'SETUPTOOLS_DO_NOT_WRAP' in script_text:
        return False
    return old_is_python_script(script_text, filename)
easy_install.is_python_script = is_python_script

setup(
    name = "kmltrack",
    description = "kmltrack converts a track (a series of lat/lon/timestamp and optional measurement values) into a kml file.",
    keywords = "kml",
    install_requires = ["python-dateutil"],
    version = "0.0.2",
    author = "Egil Moeller",
    author_email = "egil@skytruth.org",
    license = "GPL",
    url = "https://github.com/SkyTruth/kmltrack",
    packages=[
        'kmltrack',
    ],
    scripts = ["bin/kmltrack"]
)
