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
```

**Optimizing portfolio allocations**

```python
from lattice.optimize import allocate

risk_index = 8
allocation = allocate(risk_index)
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
