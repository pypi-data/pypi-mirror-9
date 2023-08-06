from distutils.core import setup
from setuptools import setup, find_packages

setup(
  name = 'webmocker',
  packages=find_packages(), # this must be the same as the name above
  version = '0.5',
  description = 'A test lib for stubbing http response',
  author = 'Shelton Paul',
  install_requires=['pretend_extended'],
  author_email = 'sheltonpaul89@gmail.com',
  url = 'https://github.com/sheltonpaul89/web-mocker', # use the URL to the github repo
  download_url = 'https://github.com/sheltonpaul89/web-mocker/tarball/0.1',
  keywords = ['web', 'stubbing', 'http','mock','Web Stubs'], # arbitrary keywords
  classifiers = [],
)