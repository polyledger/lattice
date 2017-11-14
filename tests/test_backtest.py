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
from lattice.backtest import Portfolio
from lattice.optimize import Allocator

class TestPortfolio(unittest.TestCase):
    """Test the portfolio class."""

    def test_constructor(self):
        """
        Ensure both an empty portfolio and a non-empty portfolio are
        instantiated without errors.
        """
        initial_assets = {'USD': 10000}
        portfolio = Portfolio()
        portfolio_0 = Portfolio(initial_assets)

        self.assertIsNot(portfolio, None)
        self.assertIsInstance(portfolio.assets, dict)
        self.assertIsNot(portfolio_0, None)
        self.assertEqual(portfolio_0.assets['USD'], 10000)

    def test_add_asset(self):
        """
        Ensure a few things:
        - The amount specified was actually added
        - Adding the asset created a history object
        - Ensure that the history object contains the correct information
        """
        portfolio_1 = Portfolio()
        portfolio_1.add_asset('USD', 10000)

        self.assertEqual(portfolio_1.assets['USD'], 10000)
        self.assertEqual(len(portfolio_1.history), 1)
        self.assertEqual(portfolio_1.history[0]['asset'], 'USD')
        self.assertEqual(portfolio_1.history[0]['amount'], 10000)

        with self.assertRaises(ValueError):
            portfolio_1.add_asset('USD', -10000)

    def test_get_value(self):
        """
        - Test `get_value()` with USD (the value should be unchanged)
        - Ensure the present value of coins bought in the past is correct
        - Test getting a single asset's present value
        - Ensure an error is raised if the user tries to access an asset that
          doesn't exist at the requested time
        """
        portfolio_2 = Portfolio({'USD': 10000}, '2016-01-01')
        self.assertEqual(portfolio_2.get_value(), 10000)

        # The prices at the given dates are accurate.
        portfolio_2.add_asset('BTC', 50, '2017-01-01')
        self.assertEqual(portfolio_2.get_value('2017-01-01'), 59772.0)
        portfolio_2.add_asset('ETH', 50, '2017-01-01')
        self.assertEqual(portfolio_2.get_value('2017-01-01'), 60179.0)
        portfolio_2.add_asset('LTC', 50, '2017-05-01')
        self.assertEqual(portfolio_2.get_value('2017-05-01'), 85454.0)

        # Ensure that the value before adding BTC, ETH, and LTC is the original
        # 10000 USD
        self.assertEqual(portfolio_2.get_value('2016-01-01'), 10000)

        # Ensure that getting the value of a single asset works
        self.assertEqual(portfolio_2.get_value('2017-01-01', 'BTC'), 49772.0)

        # If you try getting the value of an asset that doesn't exist in the
        # portfolio at the given time, ensure it raises an error
        with self.assertRaises(ValueError):
            portfolio_2.get_value('2015-01-01', 'USD')

        # Test that backdated assets are removed in reverse order
        portfolio_2 = Portfolio({'USD': 0}, '2017-10-01')
        portfolio_2.add_asset('USD', 100, '2017-10-28')
        portfolio_2.trade_asset(0, 'USD', 'BTC', '2017-10-28')
        portfolio_2.get_historical_value('2017-10-01', '2017-10-28', freq='D')

    def test_remove_asset(self):
        """
        Similar to `test_add_asset`, but ensure that you cannot remove an asset
        that doesn't exist.
        """
        portfolio_3 = Portfolio({'USD': 10000})
        portfolio_3.remove_asset('USD', 1000)

        self.assertEqual(portfolio_3.assets['USD'], 9000)
        self.assertEqual(len(portfolio_3.history), 2)
        self.assertEqual(portfolio_3.history[0]['asset'], 'USD')
        self.assertIsNot(portfolio_3.history[0]['amount'], -100)

        with self.assertRaises(ValueError):
            portfolio_3.remove_asset('USD', -1000)

    def test_trade_asset(self):
        """
        Test that the method removes the base and adds the quote currency.
        A trade creates two history objects, one for removing the base and one
        for adding the quote currency.
        """
        portfolio_4 = Portfolio({'USD': 10000})
        portfolio_4.trade_asset(1000, 'USD', 'BTC')
        self.assertEqual(portfolio_4.assets['USD'], 9000)
        self.assertTrue(portfolio_4.assets['BTC'] > 0)
        self.assertEqual(len(portfolio_4.history), 3)

    def test_get_historical_value(self):
        """
        Testing that the dates and values have the same length since they are
        used to create points on a chart. Also ensure that the hard limit of 22
        data points is satisfied.
        """
        portfolio_5 = Portfolio()
        portfolio_5.add_asset('BTC', 20, '2016-01-01')
        historical_value = portfolio_5.get_historical_value(
            '2016-01-01', '2017-01-01', freq='W'
        )
        self.assertTrue(len(historical_value['dates']) <= 22)
        self.assertTrue(len(historical_value['values']) <= 22)
        self.assertEqual(
            len(historical_value['dates']), len(historical_value['values'])
        )

    def test_backtest(self):
        allocations = Allocator(coins=['BTC', 'ETH', 'LTC']).allocate()

        for index, allocation in allocations.iterrows():
            portfolio = Portfolio({'USD': 100}, '2017-01-01')
            portfolio.trade_asset(allocation['ETH'], 'USD', 'ETH', '2017-01-01')
            portfolio.trade_asset(allocation['BTC'], 'USD', 'BTC', '2017-01-01')
            portfolio.trade_asset(allocation['LTC'], 'USD', 'LTC', '2017-01-01')
        data = portfolio.get_historical_value('2017-01-01', '2017-11-13', 'D')

if __name__ == '__main__':
    unittest.main()
