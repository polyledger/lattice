from setuptools import setup, find_packages

setup(
  name = 'lattice',
  packages = find_packages(),
  version = '0.1.dev7',
  description = 'A cryptocurrency market data utility package',
  author = 'Matthew Rosendin',
  author_email = 'matthew@polyledger.com',
  url = 'https://github.com/polyledger/lattice',
  download_url = 'https://github.com/polyledger/lattice/archive/v0.1-alpha.tar.gz',
  keywords = ['cryptocurrency', 'gdax', 'csv'],
  install_requires=[
    'requests',
    'python-dateutil'
  ],
  classifiers = [],
)
