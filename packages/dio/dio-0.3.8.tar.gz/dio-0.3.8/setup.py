import os
try:
  from setuptools import setup
except ImportError:
  from ez_setup import use_setuptools
  use_setuptools()
  from setuptools import setup

long_description = "Dio is a Python package for backing up and managing digitalocean droplets using v2 API. Written from the ground up to be compatible with Lorenzo Setale's work on https://github.com/koalalorenzo/python-digitalocean."

license = "http://opensource.org/licenses/MIT"

if os.path.isfile("README.md"):
  with open("README.md") as file:
    long_description = file.read()

if os.path.isfile("LICENSE.txt"):
  with open("LICENSE.txt") as file:
    license = file.read()

setup(
  name              = "dio",
  packages          = ["dio"],
  version           = "0.3.8",
  description       = "Python API for DigitalOcean v2.0 REST API",
  author            = "Rob Johnson",
  author_email      = "info@corndogcomputers.com",
  url               = "http://corndogcomputers.github.io/python-dio",
  install_requires  = ["requests"],
  download_url      = "https://github.com/corndogcomputers/python-dio/tarball/master",
  keywords          = ["digitalocean", "backup", "vps", "rsync", "api"],
  license           = license,
  long_description  = long_description,
)