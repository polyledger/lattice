# Lattice

[![PyPI version](https://badge.fury.io/py/lattice.svg)](https://badge.fury.io/py/lattice)

> A cryptocurrency market data utility Python package

Currently, Lattice uses the Global Digital Asset Exchange (GDAX) to download historical data and execute trades, but more data sources are planned to be included.

## Usage

**Creating CSV files from GDAX price data**

``` python
import lattice

# Retrieve BTC-USD prices between 2015-01-01 and 2017-06-1 with hourly price intervals
pipeline = lattice.HistoricRatesPipeline('BTC-USD', '2015-01-01', '2017-06-01', 3600)

# Output the data to `BTC_USD__2015_01_01__2017_06_01__hourly.csv`
pipeline.to_file("BTC_USD__2015_01_01__2017_06_01__hourly")
```

## Development

### Getting Started

**Virtual Environment**

This project uses [virtualenv](http://pypi.python.org/pypi/virtualenv) to isolate the development environment from the rest of the local filesystem. You must create the virtual environment, activate it, and deactivate it when you finish working.

- Create the virtual environment with `python3 -m venv venv`.
- Activate the virtual environment from within the project directory with `$ source venv/bin/activate`.
- Now you can install the project dependencies with `(venv) $ pip install -r requirements.txt`.
- When you are done working in the virtual environment, you can deactivate it: `(env) $ deactivate`. See the [python guide](http://docs.python-guide.org/en/latest/dev/virtualenvs/) for more information.

**Makefile**

Lattice comes with a Makefile which enables some useful commands. From the project root, run `make help` for a list of commands.

### Packaging and Distributing

See the [documentation](https://packaging.python.org/tutorials/distributing-packages/).
