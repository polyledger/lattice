# -*- coding: utf-8 -*-

"""
Test the optimize module.

To run tests for this file only, use the following command:

```
$ python -m unittest tests.test_optimize
```

You can run a specific test like so:

```
$ python -m unittest tests.test_optimize.TestOptimize.test_allocate
```
"""

import os
import unittest
import numpy as np
import pandas as pd
from datetime import datetime
from lattice.data import Manager
from lattice.optimize import Allocator

class TestOptimize(unittest.TestCase):
    """Test methods in the optimize module."""

    def test_retrieve_data(self):
        """Ensure that the data columns are ordered and named correctly"""
        df = Allocator(
            start=datetime(2017, 1, 1),
            end=datetime(2017, 10, 1)
        ).retrieve_data()
        expected = ['BCH', 'BTC', 'DASH', 'ETC', 'ETH', 'LTC', 'NEO', 'XMR',
                    'XRP', 'ZEC']
        self.assertEqual(sorted(df.columns.tolist()), expected)

    def test_data_argument(self):
        """Ensure that passing in a DataFrame works"""
        filepath = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '..',
            'lattice/datasets/day_historical.csv'
        )
        df = pd.read_csv(
            filepath_or_buffer=filepath,
            index_col=0,
            parse_dates=[0],
            infer_datetime_format=True
        )
        manager = Manager(df=df)
        allocations = Allocator(
            coins=['BTC', 'ETH', 'LTC'],
            manager=manager
        ).allocate()
        allocations = Allocator(coins=['BTC', 'ETH', 'LTC']).allocate()

    def test_coin_ordering(self):
        """Ensure that the order of the coins argument doesn't matter"""
        allocation1 = Allocator(coins=['BTC', 'BCH', 'ETH', 'LTC', 'ETC', 'NEO',
            'DASH', 'XMR', 'XRP', 'ZEC']).allocate()
        allocation2 = Allocator(coins=['ZEC', 'XRP', 'XMR', 'DASH', 'NEO',
            'ETC', 'LTC', 'ETH', 'BCH', 'BTC']).allocate()
        for column in allocation1:
            self.assertEqual(
                allocation1[column].all(),
                allocation2[column].all()
            )

    def test_allocate(self):
        """Ensure that the allocations for the given data are optimal."""
        default_allocations = Allocator().allocate()
        allocations = Allocator(coins=['BTC', 'ETH', 'LTC']).allocate()
        allocations = Allocator(coins=['XMR', 'XRP', 'ZEC']).allocate()
        allocations = Allocator(coins=['BTC', 'BCH', 'ETH', 'LTC', 'ETC', 'NEO',
            'DASH', 'XMR', 'XRP', 'ZEC']).allocate()
        self.assertEqual(
            default_allocations['ETH'].all(),
            allocations['ETH'].all()
        )

if __name__ == '__main__':
    unittest.main()
