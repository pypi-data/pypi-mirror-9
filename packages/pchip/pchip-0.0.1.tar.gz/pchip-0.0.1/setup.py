import os
from setuptools import setup

def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
  name = "pchip",
  packages = ["pchip"],
  version = "0.0.1",
  description = "Python script to notify availability of domain names",
  long_description = read('README.txt'),
  author = "Tricia Hinkson",
  author_email = "trhinkson@gmail.com",
  url = "https://github.com/hech/domain-check/",
  keywords = ["domain", "cli", "website"],
  classifiers = [
    "Programming Language :: Python",
    "Development Status :: 2 - Pre-Alpha",
    "Environment :: Other Environment",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    "Operating System :: OS Independent",
    "Topic :: Utilities"],
)