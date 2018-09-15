from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = 'lattice',
    packages = find_packages(),
    package_data = {
        'lattice': ['datasets/*.csv'],
    },
    include_package_data=True,
    version = '1.0.0',
    description = 'A cryptocurrency market data utility package',
    long_description=long_description,
    author = 'Matthew Rosendin, Farshad Miraftab',
    author_email = 'matthew.rosendin@gmail.com, fmiraftab@berkeley.edu',
    url = 'https://github.com/polyledger/lattice',
    download_url = 'https://github.com/polyledger/lattice/archive/v0.1-alpha.tar.gz',
    keywords = ['cryptocurrency', 'prices', 'analytics', 'crypto', 'data', 'wallet', 'backtest', 'csv'],
    install_requires=[
        'requests',
        'python-dateutil',
        'matplotlib',
        'pandas',
        'scipy',
        'numpy'
    ],
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
