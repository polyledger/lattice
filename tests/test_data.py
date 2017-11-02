# -*- coding: utf-8 -*-

"""
Test the data module.

To run tests for this file only, use the following command:

```
$ python -m unittest tests.test_data
```

You can run a specific test like so:

```
$ python -m unittest tests.test_data.TestGetHistoricData
```
"""

import os
import unittest
from lattice.data import get_historic_data, get_price
from lattice import util

class TestGetHistoricData(unittest.TestCase):
    """Test the data module."""

    def test_get_historic_data(self):
        get_historic_data(start='2015-01-01', end=util.current_date_string())

    def test_get_price(self):
        price = get_price('BTC', '2017-10-01')
        self.assertEqual(price, 4403.09)
        price = get_price('ETH', '2017-10-01')
        self.assertEqual(price, 303.95)

if __name__ == '__main__':
    unittest.main()
