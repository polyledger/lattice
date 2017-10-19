import unittest
import lattice

class TestPortfolio(unittest.TestCase):

    def test_constructor(self):
        initial_assets = {'USD': 10000}
        portfolio = lattice.Portfolio()
        portfolio_0 = lattice.Portfolio(initial_assets)

        self.assertIsNot(portfolio, None)
        self.assertIsInstance(portfolio.assets, dict)
        self.assertIsNot(portfolio_0, None)
        self.assertEqual(portfolio_0.assets['USD'], 10000)

    def test_add_asset(self):
        portfolio_1 = lattice.Portfolio()
        portfolio_1.add_asset('USD', 10000)

        self.assertEqual(portfolio_1.assets['USD'], 10000)
        self.assertEqual(len(portfolio_1.history), 1)
        self.assertEqual(portfolio_1.history[0]['asset'], 'USD')
        self.assertEqual(portfolio_1.history[0]['amount'], 10000)

        with self.assertRaises(ValueError):
            portfolio_1.add_asset('USD', -10000)

    def test_get_value(self):
        portfolio_2 = lattice.Portfolio({'USD': 10000}, '2016-01-01')
        self.assertEqual(portfolio_2.get_value(), 10000)

        # The prices at the given dates are accurate.
        portfolio_2.add_asset('BTC', 50, '2017-01-01')
        self.assertEqual(portfolio_2.get_value('2017-01-01'), 58513.5)
        portfolio_2.add_asset('ETH', 50, '2017-01-01')
        self.assertEqual(portfolio_2.get_value('2017-01-01'), 58927.0)
        portfolio_2.add_asset('LTC', 50, '2017-05-01')
        self.assertEqual(portfolio_2.get_value('2017-05-01'), 84041.0)

        # Ensure that the value before adding BTC, ETH, and LTC is the original 10000 USD
        self.assertEqual(portfolio_2.get_value('2016-01-01'), 10000)

        # Ensure that getting the value of a single asset works
        self.assertEqual(portfolio_2.get_value('2017-01-01', 'BTC'), 48513.5)

        # If you try getting the value of an asset that doesn't exist in the
        # portfolio at the given time, ensure it raises an error
        with self.assertRaises(ValueError):
            portfolio_2.get_value('2015-01-01', 'USD')

    def test_remove_asset(self):
        portfolio_3 = lattice.Portfolio({'USD': 10000})
        portfolio_3.remove_asset('USD', 1000)

        self.assertEqual(portfolio_3.assets['USD'], 9000)
        self.assertEqual(len(portfolio_3.history), 2)
        self.assertEqual(portfolio_3.history[0]['asset'], 'USD')
        self.assertIsNot(portfolio_3.history[0]['amount'], -100)

        with self.assertRaises(ValueError):
            portfolio_3.remove_asset('USD', -1000)

    def test_trade_asset(self):
        portfolio_4 = lattice.Portfolio({'USD': 10000})
        portfolio_4.trade_asset(1000, 'USD', 'BTC')
        self.assertEqual(portfolio_4.assets['USD'], 9000)
        self.assertTrue(portfolio_4.assets['BTC'] > 0)
        self.assertEqual(len(portfolio_4.history), 3)

    def test_get_historical_value(self):
        portfolio_5 = lattice.Portfolio()
        portfolio_5.add_asset('BTC', 20, '2016-01-01')
        hv = portfolio_5.get_historical_value('2016-01-01', '2017-01-01', freq='W', silent=True)
        self.assertTrue(len(hv['dates']) <= 22)
        self.assertTrue(len(hv['values']) <= 22)
        self.assertEqual(len(hv['dates']), len(hv['values']))

if __name__ == '__main__':
    unittest.main()
