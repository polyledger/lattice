# Lattice

[![PyPI version](https://badge.fury.io/py/lattice.svg)](https://badge.fury.io/py/lattice)

> A cryptocurrency market data utility Python package

Currently, Lattice uses the Global Digital Asset Exchange (GDAX) to download historical data and execute trades, but more data sources are planned to be included.

## Usage

**Creating CSV files from GDAX price data**

``` python
import lattice

# Configure for BTC-USD prices between 2015-01-01 and 2017-06-1 with hourly price intervals
pipeline = lattice.HistoricRatesPipeline('BTC-USD', '2015-01-01', '2017-06-01', 3600)

# Output the data to `BTC_USD__2015_01_01__2017_06_01__hourly.csv`
pipeline.to_file('BTC_USD__2015_01_01__2017_06_01__hourly')
```

## API Reference

### lattice.HistoricRatesPipeline

*class* `lattice.HistoricRatesPipeline(product, start, end, granularity)`

- This class is used to retrieve historical pricing data of cryptocurrency-fiat pairs.

Note: if start, end, and granularity are not specified then the most recent data is returned.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`product`|string|`'BTC-USD'`|A currency exchange pair|
|`start`|string|none|Start time in ISO 8601, e.g. `'2017-06-01T04:15:00'`|
|`end`|string|none|End time in ISO 8601, e.g. `'2017-07-01T04:15:00'`|
|`granularity`|int|none|Desired timeslice in seconds|

#### Methods

to_file(filename, path)

- Outputs market data to a CSV file. The column headers are time, low, high, open, close, volume.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`filename`|string|`'output'`|Optional. A filename for the market data|
|`path`|string|none|Optional. The path to a directory where the output file will be saved. If unspecified, the file will be saved in the current working directory.|

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

Ensure `wheel` and `twine` are installed. Then inside the directory,

1. `make clean-build`
1. `python setup.py sdist`
2. `python setup.py bdist_wheel`
3. `twine upload dist/*`

See the [Python documentation](https://packaging.python.org/tutorials/distributing-packages/) for more info.
