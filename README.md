# Lattice

> A cryptocurrency portfolio analytics Python package

[![Maintainability](https://api.codeclimate.com/v1/badges/ab47790d1135959e03eb/maintainability)](https://codeclimate.com/repos/59efa550adedb802cc000014/maintainability) [![Test Coverage](https://api.codeclimate.com/v1/badges/ab47790d1135959e03eb/test_coverage)](https://codeclimate.com/repos/59efa550adedb802cc000014/test_coverage)

## Installation

Install with pip:

```
$ sudo pip3 install git+https://USERNAME@github.com/polyledger/lattice.git@VERSION
```

**NOTE**: You must have your SSH access to the Polyledger organization for this method. Replace `USERNAME` with your GitHub username and `VERSION` with the version tag to install, e.g. `0.5`.

## Usage

**Backtesting trading strategies**

``` python
from datetime import datetime
from lattice.backtest import Portfolio

# Create a portfolio on October 1st 2017 with $100k
created_at = datetime(year=2017, month=10, day=1)
portfolio = Portfolio(
  assets={'USD': 100000},
  created_at=created_at
)

# Make some trades
trade_date = datetime(2017, 10, 1)
portfolio.trade_asset(39000, 'USD', 'BTC', trade_date)
portfolio.trade_asset(39000, 'USD', 'ETH', trade_date)
portfolio.trade_asset(22000, 'USD', 'LTC', trade_date)

# Get the current value
date = datetime(2017, 10, 24)
portfolio.get_value()
portfolio.get_value(date) # at a given date

# View the current portfolio
portfolio.assets
# => {'USD': 8515.5, 'BTC': 8.8335220838, 'ETH': 130.434782609, 'LTC': 423.07692307}

# View the portfolio's history
portfolio.history
# => [{'amount': 100000, 'asset': 'USD', 'datetime': '2017-10-01 00:00:00'}, {'amount': -39000, 'asset': 'USD', 'datetime': '2017-10-01 00:00:00'}, {'amount': 8.8335220838, 'asset': 'BTC', 'datetime': '2017-10-01 00:00:00'}, {'amount': -39000, 'asset': 'USD', 'datetime': '2017-10-01 00:00:00'}, {'amount': 130.434782609, 'asset': 'ETH', 'datetime': '2017-10-01'00:00:00 }, {'amount': -22000, 'asset': 'USD', 'datetime': '2017-10-01 00:00:00'}, {'amount': 423.07692307, 'asset': 'LTC', 'datetime': '2017-10-01'00:00:00 }, {'amount': -1.5, 'asset': 'BTC', 'datetime': '2017-10-24 18:57:30.665241' }, {'amount': 8515.5, 'asset': 'USD', 'datetime': '2017-10-24 18:57:30.665241' }]

# View the historical value data points
portfolio.get_historical_value(datetime(2017, 10, 1))

# Get portfolio value of all 10 portfolios for a portfolio created at the start of October
from lattice.backtest import Portfolio
from lattice.optimize import Allocator

def polyledger_portfolio_values(since):
    allocations = Allocator(coins=['BTC', 'LTC', 'ETH']).allocate()
    for index, allocation in allocations.iterrows():
        p = Portfolio({'USD': 10000}, since)
        for coin in allocation.keys():
            amount = (allocation[coin]/100) * 10000
            p.trade_asset(amount, 'USD', coin, since)
        print(p.get_value())

# Compare to Bitwise
def bitwise_portfolio_value(since):
  p = Portfolio({'USD': 10000}, since)
  bitwise_alloc = {
    'BTC': 0.6815, 'ETH': 0.1445, 'BCH': 0.0568, 'XRP': 0.0481, 'LTC': 0.0194,
    'DASH': 0.0147, 'ZEC': 0.0141, 'XMR': 0.0077, 'ETC': 0.0069, 'NEO': 0.0062
  }
  for coin, fraction in bitwise_alloc.items():
      amount = fraction * 10000
      p.trade_asset(amount, 'USD', coin, since)
  print(p.get_value())

since = datetime(year=2017, month=10, day=1)
polyledger_portfolio_values(since)
bitwise_portfolio_value(since)
```

**Optimizing portfolio allocations**

```python
from lattice.optimize import Allocator

coins = ['BTC', 'ETH', 'LTC', 'XRP']
allocator = Allocator(coins=coins)
allocations = allocator.allocate()
risk_index = 5  # Risk indices are from 0 to 5
allocations.loc[risk_index]
```

**Saving data to a CSV**

``` python
from datetime import date
from lattice.data import Manager

start = date(year=2017, month=1, day=1)
end = date(year=2017, month=6, day=1)
coins = ['BTC', 'LTC', 'ETH']
filepath = '/Users/ari/Desktop/prices.csv'

manager = Manager(coins)
df = manager.get_historic_data(start, end)
df.to_csv(filepath)
```

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

**Testing**

To run the full test suite, use `make test`. To get a code coverage report, ensure [coverage](https://coverage.readthedocs.io/en/coverage-4.4.2/) is installed and run

```
$ coverage run --source lattice setup.py test
```

To get the report,

```
$ coverage report -m
```

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
