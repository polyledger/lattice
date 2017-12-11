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

import unittest
import numpy as np
import pandas as pd
from lattice.optimize import Allocator

class TestOptimize(unittest.TestCase):
    """Test methods in the optimize module."""

    def test_retrieve_data(self):
        """Ensure that the data columns are ordered and named correctly"""
        dataframe = Allocator(start='2017-01-01', end='2017-10-01').retrieve_data()
        expected = ['BTC', 'ETH', 'BCH', 'XRP', 'LTC', 'XMR', 'ZEC', 'DASH',
                    'ETC', 'NEO']
        self.assertEqual(dataframe.columns.tolist(), expected)

    def test_data_argument(self):
        """Ensure that passing in a dataframe works"""
        data = pd.read_csv('../lattice/datasets/day_historical.csv')
        allocations = Allocator(coins=['BTC', 'ETH', 'LTC']).allocate(data=data)

    def test_allocate(self):
        """Ensure that the allocations for the given data are optimal."""
        default_allocations = Allocator().allocate()
        allocations = Allocator(coins=['BTC', 'ETH', 'LTC']).allocate()
        allocations = Allocator(coins=['XMR', 'XRP', 'ZEC']).allocate()
        allocations = Allocator(
            coins=['BTC', 'BCH', 'ETH', 'LTC', 'ETC', 'NEO', 'DASH', 'XMR', 'XRP', 'ZEC']
        ).allocate()
        self.assertEqual(default_allocations['ETH'].all(), allocations['ETH'].all())

if __name__ == '__main__':
    unittest.main()
