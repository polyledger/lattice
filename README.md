# Lattice

[![PyPI version](https://badge.fury.io/py/lattice.svg)](https://badge.fury.io/py/lattice)

> A cryptocurrency market data utility Python package

Currently, Lattice uses the Global Digital Asset Exchange (GDAX) to download historical data and execute trades, but more data sources are planned to be included. Lattice also includes a virtual market environment for backtesting trading algorithms.

## Usage

**Creating CSV files from GDAX price data**

``` python
import lattice

# Configure for BTC-USD prices between 2015-01-01 and 2017-06-1 with hourly price intervals
pipeline = lattice.HistoricRatesPipeline('BTC-USD', '2015-01-01', '2017-06-01', 3600)

# Output the data to `BTC_USD__2015_01_01__2017_06_01__hourly.csv`
pipeline.to_file('BTC_USD__2015_01_01__2017_06_01__hourly')
```

**Backtesting trading strategies**

``` python
import lattice

# Create an empty portfolio
portfolio = lattice.Portfolio()

# Add some assets
portfolio.add_asset('USD', 500)  # Added at current time
portfolio.add_asset('BTC', 100)
portfolio.add_asset('BTC', 20, '2016-01-01')  # Adds BTC to portfolio in the past

# Get the current value
portfolio.get_value()  # Returns today's value of portfolio with 500 USD and 120 BTC
portfolio.get_value('2016-01-01')  # Returns value of portfolio with 20 BTC at given date

# Remove some assets
portfolio.remove_asset('USD', 50)  # Removed at current time

# View the current portfolio
portfolio.assets
# => {'USD': 450, 'BTC': 120}

# View the portfolio's history
portfolio.history
# => [{'amount': 500, 'asset': 'USD', 'datetime': '2017-09-24 18:57:30.665223'}, {'amount': 100, 'asset': 'BTC', 'datetime': '2017-09-24 18:57:30.665223'}, {'amount': 20, 'asset': 'BTC', 'datetime': '2016-01-01'}, {'amount': -50, 'asset': 'USD', 'datetime': '2017-09-24 18:57:30.665241'}]

# Trade an asset for its real-time market value
portfolio.trade_asset(100, 'USD', 'ETH')
portfolio.assets
# => {'USD': 350, 'BTC': 120, 'ETH': 0.33032735440821853}

# View a chart of the historical value
portfolio.get_historical_value('2016-01-01', chart=True)
```

## API Reference

- [lattice.HistoricRatesPipeline](#latticehistoricratespipeline)
- [lattice.Portfolio](#latticeportfolio)

### lattice.HistoricRatesPipeline

*class* `lattice.HistoricRatesPipeline(product, start, end, granularity)`

- This class is used to retrieve historical pricing data of cryptocurrency-fiat pairs.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`product`|string|None|Required. A currency exchange pair|
|`start`|string|None|Required. Start time in ISO 8601, e.g. `'2017-06-01T04:15:00'`|
|`end`|string|Resolves to the current datetime|Optional. End time in ISO 8601, e.g. `'2017-07-01T04:15:00'`|
|`granularity`|int|`86400`|Desired timeslice in seconds. Common values are `1`, `60` (minute), `3600` (hour), and `86400` (day).|
|`silent`|bool|False|Silence console messages|

#### Methods

to_file(filename, path)

- Outputs market data to a CSV file. The column headers are time, low, high, open, close, volume.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`filename`|string|`'output'`|Optional. A filename for the market data|
|`path`|string|None|Optional. The path to a directory where the output file will be saved. If unspecified, the file will be saved in the current working directory.|

to_list()

- Outputs market data to an in-memory list. The column headers are time, low, high, open, close, volume. Use this method at your own risk.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`silent`|bool|False|Silence console messages|

### lattice.Portfolio

*class* `lattice.Portfolio(assets, created_at)`

- This class is used to represent a portfolio whose value can be determined for different datetimes, which is particularly useful for backtesting and/or predictive modeling.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`assets`|dict|`{}`|A dictionary of currency/amount key-value pairs, e.g. `{'ETH': 50}`|
|`created_at`|string|Resolves to the current datetime|Optional. A time in ISO 8601, e.g. `'2017-06-01T04:15:00'`.|

#### Attributes

assets : dict

- A dict of asset, value pairs held in the portfolio.

created_at : string

- A datetime string indicating when the portfolio was created.

history: list

- A list of dictionaries containing all changes of assets in this portfolio. The dictionaries indicate either an increase or decrease in the value of an asset and the time the change occurred.

#### Methods

add_asset(asset, amount, datetime)

- Adds a specified amount of an asset to the portfolio at the given datetime.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`asset`|string|`'USD'`|An asset name. Current acceptable values are `BTC`, `ETH`, `LTC`, and `USD`.|
|`amount`|float|`0`|The amount of the asset to add to the portfolio|
|`datetime`|string|Resolves to the current datetime|Optional. A time in ISO 8601, e.g. `'2017-06-01T04:15:00'`. Useful for backtesting|

get_value(datetime, asset)

- Gets the value of the portfolio at the specified datetime.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`datetime`|string|Resolves to the current datetime|Optional. A time in ISO 8601, e.g. `'2017-06-01T04:15:00'`. Useful for backtesting|
|`asset`|string|None|Optional. If specified, returns the value of the asset at the given time instead of the portfolio value.|

get_historical_value(start, end, freq, chart, silent)

- Returns historical value data or displays a chart of a portfolio's historical value where the y-axis is the portfolio's value and the x-axis is the date range.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`start`|string|None|Required. A time in ISO 8601, e.g. `'2017-06-01T04:15:00'`, for where the chart begins.|
|`end`|string|Resolves to the curent datetime|Optional. A time in ISO 8601, e.g. `'2017-06-01T04:15:00'`, for where the chart ends.|
|`freq`|string|`'D'`|The frequency of data points. See [Offset Aliases](http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases) for valid values.|
|`chart`|bool|False|Returns historical value data if `True`, otherwise displays a chart.|
|`date_format`|string|`'%m-%d-%Y'`|The format for the time x-axis labels. See the [strftime](http://strftime.org/) documentation for reference.|
|`silent`|bool|False|Optional. Silence console messages|

trade_asset(amount, from_asset, to_asset, datetime)

- Exchanges one asset for another at the given datetime.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`amount`|float|`0`|The amount of `from_asset` to exchange|
|`from_asset`|string|None|Required. The traded asset, e.g. `USD`, `BTC`, `ETH`, `LTC`|
|`to_asset`|string|None|Required. The received asset, e.g. `USD`, `BTC`, `ETH`, `LTC`|
|`datetime`|string|Resolves to the current datetime|Optional. A time in ISO 8601, e.g. `'2017-06-01T04:15:00'`. Useful for backtesting|

remove_asset(asset, amount, datetime)

- Removes a specified amount of an asset to the portfolio at the given datetime.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`asset`|string|`'USD'`|An asset name. Current acceptable values are `BTC`, `ETH`, `LTC`, and `USD`.|
|`amount`|float|`0`|The amount of the asset to remove from the portfolio|
|`datetime`|string|Resolves to the current datetime|Optional. A time in ISO 8601, e.g. `'2017-06-01T04:15:00'`. Useful for backtesting|

## Development

### Getting Started

**Virtual Environment**

This project uses [virtualenv](http://pypi.python.org/pypi/virtualenv) to isolate the development environment from the rest of the local filesystem. You must create the virtual environment, activate it, and deactivate it when you finish working.

- Create the virtual environment with `python3 -m venv venv`.
- Activate the virtual environment from within the project directory with `$ source venv/bin/activate`.
- Now you can install the project dependencies with `(venv) $ pip3 install -r requirements.txt`.
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
