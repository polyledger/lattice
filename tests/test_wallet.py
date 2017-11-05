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

    def test_generate_private_key(self):
        password = 'password'
        private_key = generate_private_key(password)

        self.assertEqual(len(private_key), 64)

    def test_generate_public_key(self):
        password = 'password'
        private_key = generate_private_key(password)
        public_key = generate_public_key(private_key)

class TestJacobianPoint(unittest.TestCase):
    """Test the jacobian point class."""

    Gx = 10
    Gy = 15
    G = (Gx, Gy)

    def test_jacobian_point(self):
        X, Y, Z = Gx, Gy, 1
        j = JacobianPoint(X, Y, Z)
        JacobianPoint.double(j)
        j.inverse(G[1], P)
        j * 5

if __name__ == '__main__':
    unittest.main()
