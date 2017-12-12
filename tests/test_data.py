# -*- coding: utf-8 -*-

"""
Test the data module.

To run tests for this file only, use the following command:

```
$ python -m unittest tests.test_data
```

You can run a specific test like so:

```
$ python -m unittest tests.test_data.TestManager
```
"""

import os
import unittest
import pandas as pd
from datetime import date
from lattice.data import Manager
from lattice import util

class TestManager(unittest.TestCase):
    """Test the Manager class."""

    def test_constructor(self):
        """The constructor initializes a Manager class instance"""
        manager = Manager()
        self.assertIsInstance(manager, Manager)

    def test_get_historic_data(self):
        """Historic data is retrieved"""
        # Test case where existing CSV is read
        manager = Manager()
        historic_data = manager.get_historic_data()
        self.assertIsInstance(historic_data, pd.DataFrame)

        # Test case where a DataFrame is passed
        df = pd.DataFrame()
        manager = Manager(df=df)
        historic_data = manager.get_historic_data()
        self.assertIsInstance(historic_data, pd.DataFrame)

    def test_get_historic_data_raises(self):
        """Historic data should raise when invalid end date is passed"""
        manager = Manager()
        start = date(2015, 1, 1)
        end = date(2020, 1, 1)

        with self.assertRaises(ValueError):
            manager.get_historic_data(start=start, end=end)

    def test_get_price(self):
        """Prices are retrieved"""
        # Test case where existing CSV is read
        manager = Manager()
        price = manager.get_price('BTC', date(2017, 10, 1))
        self.assertEqual(price, 4403.09)
        price = manager.get_price('ETH', date(2017, 10, 1))
        self.assertEqual(price, 303.95)

        # Test case where a DataFrame is passed
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..',
            'lattice/datasets/day_historical.csv'
        )
        df = pd.read_csv(
            filepath_or_buffer=filepath,
            index_col=0,
            parse_dates=[0],
            infer_datetime_format=True
        )
        manager = Manager(df=df)
        price = manager.get_price('BTC', date(2017, 10, 1))
        self.assertEqual(price, 4403.09)
        price = manager.get_price('ETH', date(2017, 10, 1))
        self.assertEqual(price, 303.95)

if __name__ == '__main__':
    unittest.main()
