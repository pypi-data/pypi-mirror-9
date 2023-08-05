from setuptools import setup

setup(
  name = 'frenetic',
  packages = [ 'frenetic' ],
  version = '0.1.1',
  description = 'Python bindings for Frenetic',
  author = 'Arjun Guha',
  author_email = 'arjun@cs.umass.edu',
  url = 'https://github.com/arjunguha/frenetic-python',
  download_url = 'https://github.com/arjunguha/frenetic-python/tarball/master',
  install_requires = [ 'tornado' ],
  classifiers = []
)
