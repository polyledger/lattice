from setuptools import setup, find_packages

setup(
  name = 'lattice',
  packages = find_packages(),
  version = '0.3.3',
  description = 'A cryptocurrency market data utility package',
  author = 'Matthew Rosendin, Farshad Miraftab',
  author_email = 'matthew@polyledger.com, farshad@polyledger.com',
  url = 'https://github.com/polyledger/lattice',
  download_url = 'https://github.com/polyledger/lattice/archive/v0.1-alpha.tar.gz',
  keywords = ['cryptocurrency', 'gdax', 'csv'],
  install_requires=[
    'requests',
    'python-dateutil',
    'matplotlib',
    'pandas',
    'scipy',
    'numpy'
  ],
  classifiers = [],
)
