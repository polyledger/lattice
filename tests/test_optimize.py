# -*- coding: utf-8 -*-

"""
Test the optimize module.
"""

import unittest
import numpy as np
import pandas as pd
from lattice.optimize import allocate, retrieve_data

class TestOptimize(unittest.TestCase):
    """Test methods in the optimize module."""

    def test_retrieve_data(self):
        """Ensure that the data columns are ordered and named correctly"""
        dataframe = retrieve_data(start='2017-01-01', end='2017-02-01')
        expected = ['time', 'BTC_close', 'ETH_close', 'LTC_close']
        self.assertEqual(dataframe.columns.tolist(), expected)

    def test_allocate(self):
        """Ensure that the allocations for the given data are optimal."""
        risk_index = 1
        data = [
            [1508396400, 4743.94, 389.20, 73.23],
            [1508482800, 4581.98, 384.10, 66.03],
            [1508569200, 4599.00, 372.48, 63.75]
        ]
        columns = ['time', 'BTC_close', 'ETH_close', 'LTC_close']
        dataframe = pd.DataFrame(data, columns=columns)
        dataframe.replace(0, np.nan, inplace=True)
        allocation = allocate(risk_index, dataframe=dataframe)

        self.assertEqual(allocation['BTC'], 0.181000)
        self.assertEqual(allocation['ETH'], 0.697000)
        self.assertEqual(allocation['LTC'], 0.122000)

if __name__ == '__main__':
    unittest.main()
