# -*- coding: utf-8 -*-

"""
This module allows the creation of wallets for various native cryptos.
"""

from __future__ import print_function
import hashlib
import binascii


"""
Elliptic curve parameters (secp256k1)
See https://en.bitcoin.it/wiki/Secp256k1

The curve E: y^2 = x^3 + ax + b over Fp

P is the characteristic of the finite field
G is the base (or generator) point
N is a prime number, called the order (number of points in E(Fp))
H is the cofactor

Hexadecimal representations:
  P = FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE FFFFFC2F
  A = 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000
  B = 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000007
  G = 02 79BE667E F9DCBBAC 55A06295 CE870B07 029BFCDB 2DCE28D9 59F2815B 16F81798
  N = FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFE BAAEDCE6 AF48A03B BFD25E8C D0364141
  H = 01
"""
P = 2 ** 256 - 2 ** 32 - 2 ** 9 - 2 ** 8 - 2 ** 7 - 2 ** 6 - 2 ** 4 - 1
a = 0
b = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (Gx, Gy)
n = 115792089237316195423570985008687907852837564279074904382605163141518161494337

def generate_private_key(password):
    """
    Generates a private key based on the password.

    SHA-256 is a member of the SHA-2 cryptographic hash functions designed by
    the NSA. SHA stands for Secure Hash Algorithm. The password is converted
    to bytes and hashed with SHA-256. The binary output is converted to a hex
    representation.

    Args:
        data (str): The data to be hashed with SHA-256.

    Returns:
        bytes: The hexadecimal representation of the hashed binary data.
    """
    binary_data = bytes(password, 'utf-8')
    hash_object = hashlib.sha256(binary_data)
    message_digest_bin = hash_object.digest()
    message_digest_hex = binascii.hexlify(message_digest_bin)
    return message_digest_hex

def generate_public_key(private_key):
    """
    Generates a public key from the hex-encoded private key using elliptic
    curve cryptography. The private key is multiplied by a predetermined point
    on the elliptic curve called the generator point, G, resulting in the
    corresponding private key. The generator point is always the same for all
    Bitcoin users.

    Jacobian coordinates are used to represent the elliptic curve point G.
    https://en.wikibooks.org/wiki/Cryptography/Prime_Curve/Jacobian_Coordinates

    The exponentiating by squaring (also known by double-and-add) method is
    used for the elliptic curve multiplication that results in the public key.
    https://en.wikipedia.org/wiki/Exponentiation_by_squaring

    Args:
        private_key (bytes): UTF-8 encoded hexadecimal
    Returns:

    """
    private_key = int(private_key, 16)
    if private_key >= n:
        raise Exception('Invalid private key.')

    G = JacobianPoint(Gx, Gy, 1)
    public_key = G * private_key

class JacobianPoint(object):
    """
    Defines a Jacobian coordinate system point and operations that can be
    performed. Algorithms defined in this link:
    https://en.wikibooks.org/wiki/Cryptography/Prime_Curve/Jacobian_Coordinates
    """

    POINT_AT_INFINITY = (1, 1, 0)

    def __init__(self, X, Y, Z):
        self.X = X
        self.Y = Y
        self.Z = Z

    def __add__(self, other):
        X1, Y1, Z1 = self.X, self.Y, self.Z
        X2, Y2, Z2 = other.X, other.Y, other.Z
        U1 = (X1 * Z2 ** 2) % P
        U2 = (X2 * Z1 ** 2) % P
        S1 = (Y1 * Z2 ** 3) % P
        S2 = (Y2 * Z1 ** 3) % P
        if U1 == U2:
            if S1 != S2:
                return POINT_AT_INFINITY
            else:
                return self.double((X1, Y1, Z1))
        H = U2 - U1
        R = S2 - S1
        X3 = (R ** 2 - H ** 3 - 2 * U1 * H ** 2) % P
        Y3 = (R * (U1 * H ** 2 - X3) - S1 * H ** 3) % P
        Z3 = H * Z1 * Z2
        return JacobianPoint((X3, Y3, Z3))

    def __mul__(self, N):
        X1, Y1, Z1 = self.X, self.Y, self.Z

        if Y1 == 0 or P == 0:
            return JacobianPoint(0, 0, 1)
        elif N == 1:
            return JacobianPoint(X1, Y1, Z1)
        elif N < 0 or N >= n:
            return self * N % n
        elif (N % 2) == 0:
            return JacobianPoint.double(AffinePoint(*G).to_jacobian() * (N//2))
        elif (N % 2) == 1:
            return JacobianPoint.double(AffinePoint(*G).to_jacobian() * (N//2))

    def __repr__(self):
        return "<JacobianPoint (%s, %s, %s)>" %(self.X, self.Y, self.Z)

    @staticmethod
    def double(point):
        X1, Y1, Z1 = point.X, point.Y, point.Z

        if Y1 == 0:
            return POINT_AT_INFINITY
        S = (4 * X1 * Y1 ** 2) % P
        M = (3 * X1 ** 2 + a * Z1 ** 4) % P
        X3 = (M ** 2 - 2 * S) % P
        Y3 = (M * (S - X3) - 8 * Y1 ** 4) % P
        Z3 = (2 * Y1 * Z1) % P
        return JacobianPoint(X3, Y3, Z3)

    @staticmethod
    def inverse(N, P):
        """
        Returns the modular inverse of an integer with respect to the field
        characteristic, P.

        Use the Extended Euclidean Algorithm:
        https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
        """

        C, D = N, P
        X1, X2, Y1, Y2 = 1, 0, 0, 1

        while C != 0:
            Q, C, D = divmod(D, C) + (C,)
            X1, X2 = X2, X1 - Q * X2
            Y1, Y2 = Y2, Y1 - Q * Y2

        if N == 1:
            return X1 % P

    def to_affine(self):
        X, Y, Z = self.x, self.y, self.inverse(self.z, P)
        return ((X * Z ** 2) % P, (Y * Z ** 3) % P)

class AffinePoint(object):

    def __init__(self, X, Y):
        self.X = X
        self.Y = Y

    def __add__(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if not isinstance(other, AffinePoint):
            return False
        return self.X == other.X and self.X == other.Y

    def __ne__(self, other):
        return not (self == other)

    def __mul__(self):
        raise NotImplementedError()

    def __repr__(self):
        return "<AffinePoint (%s, %s)>" % (self.X, self.Y)

    def double(self):
        raise NotImplementedError()

    def to_jacobian(self):
        if not self:
            return JacobianPoint(X=0, Y=0, Z=0)
        return JacobianPoint(X=self.X, Y=self.Y, Z=1)
