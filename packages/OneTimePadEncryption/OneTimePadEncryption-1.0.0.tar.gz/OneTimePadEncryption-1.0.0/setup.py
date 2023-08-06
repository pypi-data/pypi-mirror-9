import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
  name = 'OneTimePadEncryption',
  packages = ['OneTimePadEncryptionUtility'],
  version = '1.0.0',
  author = 'Marc Santiago',
  author_email = 'marcanthonysanti@gmail.com',
  url = 'https://github.com/marcsantiago/one-time-pad-encryption', 
  download_url = 'https://github.com/marcsantiago/one-time-pad-encryption/tarball/0.1', 
  keywords = ['encryption', 'one time pad'], 
  long_description=read('README.txt'),
  classifiers = [],
)