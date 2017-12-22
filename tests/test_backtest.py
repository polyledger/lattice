# -*- coding: utf-8 -*-

"""
Test the backtest module.

To run tests for this file only, use the following command:

```
$ python -m unittest tests.test_backtest
```

You can run a specific test like so:

```
$ python -m unittest tests.test_backtest.TestPortfolio.test_add_asset
```
"""

import unittest
from datetime import datetime
from lattice.backtest import Portfolio
from lattice.optimize import Allocator

class TestPortfolio(unittest.TestCase):
    """Test the portfolio class."""

    def test_constructor(self):
        """Portfolios are instantiated without errors"""
        portfolio = Portfolio()
        self.assertIsNot(portfolio, None)
        self.assertIsInstance(portfolio.assets, dict)

        portfolio = Portfolio({'USD': 10000})
        self.assertIsNot(portfolio, None)
        self.assertEqual(portfolio.assets['USD'], 10000)

    def test_add_asset(self):
        """Assets are added"""
        portfolio = Portfolio()
        portfolio.add_asset('USD', 10000)

        self.assertEqual(portfolio.assets['USD'], 10000)
        self.assertEqual(len(portfolio.history), 1)
        self.assertEqual(portfolio.history[0]['asset'], 'USD')
        self.assertEqual(portfolio.history[0]['amount'], 10000)

        with self.assertRaises(ValueError):
            portfolio.add_asset('USD', -10000)

    def test_get_value(self):
        """Value of a portfolio is correct"""
        portfolio = Portfolio({'USD': 10000}, datetime(2016, 1, 1))
        self.assertEqual(portfolio.get_value(), 10000)

        # The prices at the given dates are accurate.
        timestamp = datetime(2017, 1, 1)
        portfolio.add_asset('BTC', 50, timestamp)
        self.assertEqual(portfolio.get_value(timestamp), 59772.0)

        portfolio.add_asset('ETH', 50, timestamp)
        self.assertEqual(portfolio.get_value(timestamp), 60179.0)

        timestamp = datetime(2017, 5, 1)
        portfolio.add_asset('LTC', 50, timestamp)
        self.assertEqual(portfolio.get_value(timestamp), 85454.0)

        # Ensure that the value before adding BTC, ETH, and LTC is the original
        # 10000 USD
        self.assertEqual(portfolio.get_value(datetime(2016, 1, 1)), 10000)

        # Ensure that getting the value of a single asset works
        timestamp = datetime(2017, 1, 1)
        self.assertEqual(portfolio.get_value(timestamp, 'BTC'), 49772.0)

        # If you try getting the value of an asset that doesn't exist in the
        # portfolio at the given time, ensure it raises an error
        with self.assertRaises(ValueError):
            portfolio.get_value(datetime(2015, 1, 1), 'USD')

        # Test that backdated assets are removed in reverse order
        start = datetime(2017, 10, 1)
        end = datetime(2017, 10, 28)
        portfolio = Portfolio({'USD': 0}, start)
        portfolio.add_asset('USD', 100, end)
        portfolio.trade_asset(0, 'USD', 'BTC', end)
        portfolio.get_historical_value(start, end, freq='D')

    def test_remove_asset(self):
        """Assets are removed"""
        portfolio = Portfolio({'USD': 10000})
        portfolio.remove_asset('USD', 1000)

        self.assertEqual(portfolio.assets['USD'], 9000)
        self.assertEqual(len(portfolio.history), 2)
        self.assertEqual(portfolio.history[0]['asset'], 'USD')
        self.assertIsNot(portfolio.history[0]['amount'], -100)

        """Can't remove a negative amount of an asset"""
        with self.assertRaises(ValueError):
            portfolio.remove_asset('USD', -1000)

        """Can't remove an asset before it was added"""
        portfolio = Portfolio({'BTC': 1}, created_at=datetime(2017, 1, 1))
        with self.assertRaises(ValueError):
            portfolio.remove_asset(
                asset='BTC',
                amount=1,
                timestamp=datetime(2016, 1, 1)
            )

    def test_trade_asset(self):
        """Assets are traded"""
        portfolio = Portfolio({'USD': 10000})
        portfolio.trade_asset(1000, 'USD', 'BTC')
        self.assertEqual(portfolio.assets['USD'], 9000)
        self.assertTrue(portfolio.assets['BTC'] > 0)
        self.assertEqual(len(portfolio.history), 3)

        """Can't trade an asset before it existed"""
        portfolio = Portfolio({'USD': 10000})
        with self.assertRaises(ValueError):
            portfolio.trade_asset(1000, 'USD', 'BCH', datetime(2017, 1, 1))

    def test_get_historical_value(self):
        """Historical value data of portfolio is retrieved"""
        portfolio = Portfolio()
        portfolio.add_asset('BTC', 20, datetime(2016, 1, 1))
        historical_value = portfolio.get_historical_value(
            start=datetime(2016, 1, 1),
            end=datetime(2017, 1, 1),
            freq='W'
        )
        self.assertTrue(len(historical_value['dates']) <= 22)
        self.assertTrue(len(historical_value['values']) <= 22)
        self.assertEqual(
            len(historical_value['dates']),
            len(historical_value['values'])
        )
        historical_value = portfolio.get_historical_value(
            start=datetime(2010, 1, 1),
            end=datetime(2017, 11, 28),
            freq='D'
        )
        self.assertTrue(len(historical_value['dates']) <= 22)
        self.assertTrue(len(historical_value['values']) <= 22)
        self.assertEqual(
            len(historical_value['dates']),
            len(historical_value['values'])
        )

    def test_backtest(self):
        """Portfolios are properly backtested"""
        start = datetime(2017, 1, 1)
        end = datetime(2017, 11, 13)

        coins = ['BTC', 'ETH', 'LTC']
        allocations = Allocator(coins=coins).allocate()

        for index, allocation in allocations.iterrows():
            portfolio = Portfolio({'USD': 100}, start)
            for coin in coins:
                portfolio.trade_asset(allocation[coin], 'USD', coin, start)

        data = portfolio.get_historical_value(
            start=start,
            end=end,
            freq='D'
        )

        coins = ['BTC', 'ETH', 'LTC', 'ZEC', 'XMR', 'ETC', 'DASH']
        allocations = Allocator(coins=coins).allocate()

        for index, allocation in allocations.iterrows():
            portfolio = Portfolio({'USD': 100}, start)
            for coin in coins:
                portfolio.trade_asset(allocation[coin], 'USD', coin, start)
        data = portfolio.get_historical_value(start, end, 'D')

        """Coins not in existence are purchased at time of fork/ICO"""
        coins = ['BTC', 'ETH', 'LTC', 'ZEC', 'XMR', 'ETC', 'DASH', 'BCH', 'NEO']
        allocations = Allocator(coins=coins).allocate()

        for index, allocation in allocations.iterrows():
            portfolio = Portfolio({'USD': 100}, start)
            for coin in coins:
                portfolio.trade_asset(allocation[coin], 'USD', coin, start)
        data = portfolio.get_historical_value(start, end, 'D')

if __name__ == '__main__':
    unittest.main()
