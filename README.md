# Lattice

> A cryptocurrency analytics Python package

Currently, Lattice uses the Global Digital Asset Exchange (GDAX) to download historical data and execute trades, but more data sources are planned to be included. Lattice also includes a virtual market environment for backtesting trading algorithms.

## Usage

**Creating CSV files from GDAX price data**

``` python
from lattice.data import HistoricRatesPipeline

# Configure for BTC-USD prices between 2015-01-01 and 2017-06-1 with hourly price intervals
pipeline = HistoricRatesPipeline('BTC-USD', '2015-01-01', '2017-06-01', 3600)

# Output the data to `BTC_USD__2015_01_01__2017_06_01__hourly.csv`
pipeline.to_file('BTC_USD__2015_01_01__2017_06_01__hourly')
```

**Backtesting trading strategies**

``` python
from lattice.backtest import Portfolio

# Create a portfolio on October 1st 2017 with $100k
portfolio = Portfolio({'USD': 100000}, '2017-10-01')

# Make some trades
portfolio.trade_asset(39000, 'USD', 'BTC', '2017-10-01')
portfolio.trade_asset(39000, 'USD', 'ETH', '2017-10-01')
portfolio.trade_asset(22000, 'USD', 'LTC', '2017-10-01')

# Get the current value
portfolio.get_value()
portfolio.get_value('2017-10-24') # at a given date

# Remove some assets
portfolio.trade_asset(1.5, 'BTC', 'USD')  # Traded at current time

# View the current portfolio
portfolio.assets
# => {'USD': 8515.5, 'BTC': 8.8335220838, 'ETH': 130.434782609, 'LTC': 423.07692307}

# View the portfolio's history
portfolio.history
# => [{'amount': 100000, 'asset': 'USD', 'datetime': '2017-10-01 00:00:00'}, {'amount': -39000, 'asset': 'USD', 'datetime': '2017-10-01 00:00:00'}, {'amount': 8.8335220838, 'asset': 'BTC', 'datetime': '2017-10-01 00:00:00'}, {'amount': -39000, 'asset': 'USD', 'datetime': '2017-10-01 00:00:00'}, {'amount': 130.434782609, 'asset': 'ETH', 'datetime': '2017-10-01'00:00:00 }, {'amount': -22000, 'asset': 'USD', 'datetime': '2017-10-01 00:00:00'}, {'amount': 423.07692307, 'asset': 'LTC', 'datetime': '2017-10-01'00:00:00 }, {'amount': -1.5, 'asset': 'BTC', 'datetime': '2017-10-24 18:57:30.665241' }, {'amount': 8515.5, 'asset': 'USD', 'datetime': '2017-10-24 18:57:30.665241' }]

# View a chart of the historical value
portfolio.get_historical_value('2017-10-01', chart=True)
```

## API Reference

- [lattice.backtest.Portfolio](#latticebacktestportfolio)
- [lattice.data.HistoricRatesPipeline](#latticedatahistoricratespipeline)
- [lattice.optimize.allocate](#latticeoptimizeallocate)

### lattice.backtest.Portfolio

*class* `lattice.backtest.Portfolio(assets, created_at)`

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

### lattice.data.HistoricRatesPipeline

*class* `lattice.data.HistoricRatesPipeline(product, start, end, granularity)`

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

### lattice.optimize.allocate

allocate(risk_index, dataframe)

- Allocates a portfolio given the user's risk tolerance.

|Parameter|Type|Default|Description|
|---------|----|-------|-----------|
|`risk_index`|integer|None|A risk score from 1-10.|
|`dataframe`|Pandas.DataFrame|None|Optional. A Pandas DataFrame with a timestamp index and closing prices of coins as columns.|

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

#### GitHub Release

Before tagging a release, ensure that `make test` and `make lint` pass without errors.

```
$ git tag -a MAJOR.MINOR.PATCH -m "Description of release goes here"
$ git push --tags
```

Although not necessary, you should also update the version in `setup.py`.

#### PyPi

Ensure `wheel` and `twine` are installed. Then inside the directory,

1. `make clean-build`
1. `python setup.py sdist`
2. `python setup.py bdist_wheel`
3. `twine upload dist/*`

See the [Python documentation](https://packaging.python.org/tutorials/distributing-packages/) for more info.
