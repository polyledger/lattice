# -*- coding: utf-8 -*-

"""
Test the data module.

To run tests for this file only, use the following command:

```
$ python -m unittest tests.test_wallet
```

You can run a specific test like so:

```
$ python -m unittest tests.test_wallet.TestWallet
```
"""

import unittest
from lattice.wallet import *

class TestWallet(unittest.TestCase):
    """Test the wallet class."""

    def test_wallet(self):
        wallet = Wallet()
        private_key = wallet.private_key
        self.assertEqual(len(private_key), 64)
        public_key = wallet.public_key
        self.assertEqual(len(public_key), 130)

class TestJacobianPoint(unittest.TestCase):
    """Test the jacobian point class."""

    def test_jacobian_point(self):
        Gx = 10
        Gy = 15
        X, Y, Z = Gx, Gy, 1
        j = JacobianPoint(X, Y, Z)
        j.double()
        j.inverse(X)
        j * 5

class TestAffinePoint(unittest.TestCase):
    """Tests the affine point class."""

    def test_affine_point(self):
        Gx = 10
        Gy = 15
        X, Y = Gx, Gy
        p = AffinePoint(X, Y)
        p.double()
        p.inverse(X)
        p * 5

if __name__ == '__main__':
    unittest.main()
