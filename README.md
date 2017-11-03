# Lattice

> A cryptocurrency portfolio analytics Python package

## Usage

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

# Get portfolio value of all 10 portfolios for a portfolio created at the start of October
from lattice.backtest import Portfolio
from lattice.optimize import allocate

def polyledger_portfolio_values(since):
    allocations = allocate()
    for index, allocation in allocations.iterrows():
        p = Portfolio({'USD': 10000}, since)
        for coin in allocation.keys():
            p.trade_asset(allocation[coin] * 10000, 'USD', coin, since)
        print(p.get_value())

# Compare to Bitwise
def bitwise_portfolio_value(since):
  p = Portfolio({'USD': 10000}, since)
  bitwise_alloc = {
    'BTC': 0.6815, 'ETH': 0.1445, 'BCH': 0.0568, 'XRP': 0.0481, 'LTC': 0.0194,
    'DASH': 0.0147, 'ZEC': 0.0141, 'XMR': 0.0077, 'ETC': 0.0069, 'NEO': 0.0062
  }
  for coin, percent in bitwise_alloc.items():
      p.trade_asset(percent * 10000, 'USD', coin, since)
  print(p.get_value())

polyledger_portfolio_values('2017-10-01')
bitwise_portfolio_value('2017-10-01')
```

**Optimizing portfolio allocations**

```python
from lattice.optimize import allocate

allocations = allocate()
risk_index = 5 # Risk indexes are from 1 to 10
allocations.loc[risk_index - 1]
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
