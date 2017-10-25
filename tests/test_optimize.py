import unittest
import numpy as np
import pandas as pd
from lattice.optimize import allocate, retrieve_data

class TestOptimize(unittest.TestCase):

    def test_retrieve_data(self):
        df = retrieve_data()
        expected = ['BTC_close', 'ETH_close', 'LTC_close']
        self.assertEqual(df.columns, expected)

    def test_allocate(self):
        risk_index = 0
        data = [
            [1508396400, 4743.94, 389.20, 73.23],
            [1508482800, 4581.98, 384.10, 66.03],
            [1508569200, 4599.00, 372.48, 63.75]
        ]
        columns = ['time', 'BTC_close', 'ETH_close', 'LTC_close']
        df = pd.DataFrame(data, columns=columns)
        df.replace(0, np.nan, inplace=True)
        allocation = allocate(risk_index, df=df)

        self.assertEqual(allocation['BTC'], 0.181000)
        self.assertEqual(allocation['ETH'], 0.697000)
        self.assertEqual(allocation['LTC'], 0.122000)

if __name__ == '__main__':
    unittest.main()
