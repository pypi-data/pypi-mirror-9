from distutils.core import setup
from setuptools import find_packages

setup(
  name = 'pyCore',
  packages = find_packages(),
  version = '0.9',
  description = 'OverCluster API Library',
  author = 'Maciej & Marta Nabozny',
  author_email = 'mn@mnabozny.pl',
  url = 'http://cloudover.org/pycore/',
  download_url = 'https://github.com/cloudOver/PyCloud/archive/master.zip',
  keywords = ['overcluster', 'cloudover', 'cloud'],
  classifiers = [],
  install_requires = ['requests']
)
