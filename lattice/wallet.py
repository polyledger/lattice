# -*- coding: utf-8 -*-

"""
This module allows the creation of wallets for various native cryptos.
"""

from __future__ import print_function
import hashlib
import binascii
import base64
import os


class secp256k1(object):
    """
    Elliptic curve with Secp256k1 standard parameters
    See https://en.bitcoin.it/wiki/Secp256k1

    This is the curve E: y^2 = x^3 + ax + b over Fp

    P is the characteristic of the finite field
    G is the base (or generator) point
    N is a prime number, called the order (number of points in E(Fp))
    H is the cofactor
    """

    def __init__(self):
        self.P = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
        self.a = 0
        self.b = 7
        self.N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
        self.Gx = 0x79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798
        self.Gy = 0x483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
        self.G = (self.Gx, self.Gy)
        self.H = 1

    @property
    def base_point(self):
        """
        Returns the base point for this curve.

        Returns:
            JacobianPoint: The base point.
        """
        return JacobianPoint(self, self.Gx, self.Gy)

    def inverse(self, N):
        """
        Returns the modular inverse of an integer with respect to the field
        characteristic, P.

        Use the Extended Euclidean Algorithm:
        https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
        """
        if N == 0:
            return 0
        lm, hm = 1, 0
        low, high = N % self.P, self.P
        while low > 1:
            r = high//low
            nm, new = hm - lm * r, high - low * r
            lm, low, hm, high = nm, new, lm, low

        return lm % self.P

    def is_on_curve(self, point):
        """
        Checks whether a point is on the curve.

        Args:
            point (AffinePoint): Point to be checked.

        Returns:
            bool: True if point is on the curve, False otherwise.
        """
        X, Y = point.X, point.Y
        return (
                pow(Y, 2, self.P) - pow(X, 3, self.P) - self.a * X - self.b
            ) % self.P == 0


class Wallet(secp256k1):
    """
    Creates a wallet with a public/private key pair.
    """

    def __init__(self):
        super().__init__()
        self.private_key = self.generate_private_key()
        self.public_key = self.generate_public_key()
        self.address = self.generate_address()

    def generate_private_key(self):
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
        random_string = base64.b64encode(os.urandom(4096)).decode('utf-8')
        binary_data = bytes(random_string, 'utf-8')
        hash_object = hashlib.sha256(binary_data)
        message_digest_bin = hash_object.digest()
        message_digest_hex = binascii.hexlify(message_digest_bin)
        return message_digest_hex

    def generate_public_key(self):
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

        Bitcoin public keys are 65 bytes. The first byte is 0x04, next 32
        bytes correspond to the X coordinate, and last 32 bytes correspond
        to the Y coordinate. They are typically encoded as 130-length hex
        characters.

        Args:
            private_key (bytes): UTF-8 encoded hexadecimal
        Returns:
            str: The public key in hexadecimal representation.
        """
        private_key = int(self.private_key, 16)
        if private_key >= self.N:
            raise Exception('Invalid private key.')

        G = JacobianPoint(self.Gx, self.Gy, 1)
        public_key = G * private_key

        x_hex = '{0:0{1}x}'.format(public_key.X, 64)
        y_hex = '{0:0{1}x}'.format(public_key.Y, 64)
        return '04' + x_hex + y_hex

    def generate_address(self):
        """
        Creates a Bitcoin address from the public key.
        
        Details of the steps for creating the address are outlined in this link:
        https://en.bitcoin.it/wiki/Technical_background_of_version_1_Bitcoin_addresses
        
        The last step is Base58Check encoding, which is similar to Base64 encoding but
        slightly different to create a more human-readable string where '1' and 'l' won't
        get confused. More on Base64Check encoding here:
        https://en.bitcoin.it/wiki/Base58Check_encoding
        """
        binary_pubkey = binascii.unhexlify(self.public_key)
        binary_digest_sha256 = hashlib.sha256(binary_pubkey).digest()
        binary_digest_ripemd160 = hashlib.new('ripemd160', binary_digest_sha256).digest()

        binary_version_byte = bytes([0])
        binary_with_version_key = binary_version_byte + binary_digest_ripemd160

        checksum_intermed = hashlib.sha256(binary_with_version_key).digest()
        checksum_intermed = hashlib.sha256(checksum_intermed).digest()
        checksum = checksum_intermed[:4]

        binary_address = binary_digest_ripemd160 + checksum

        leading_zero_bytes = 0
        
        for char in binary_address:
            if char == 0:
                leading_zero_bytes += 1

        inp = binary_address + checksum
        result = 0

        while len(inp) > 0:
            result *= 256
            result += inp[0]
            inp = inp[1:]
        
        result_bytes = bytes()
        while result > 0:
            curcode = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'[result % 58]
            result_bytes = bytes([ord(curcode)]) + result_bytes
            result //= 58

        pad_size = 0 - len(result_bytes)
        padding_element = b'1'

        if pad_size > 0:
            result_bytes = padding_element * pad_size + result_bytes
        result = ''.join([chr(y) for y in result_bytes])
        address = '1' * leading_zero_bytes + result
        return address

class JacobianPoint(secp256k1):
    """
    Defines a Jacobian coordinate system point and operations that can be
    performed. Algorithms defined in this link:
    https://en.wikibooks.org/wiki/Cryptography/Prime_Curve/Jacobian_Coordinates
    """

    POINT_AT_INFINITY = (1, 1, 0)

    def __init__(self, X, Y, Z):
        super().__init__()
        self.X = X
        self.Y = Y
        self.Z = Z

    def __add__(self, other):
        X1, Y1, Z1 = self.X, self.Y, self.Z
        X2, Y2, Z2 = other.X, other.Y, other.Z
        U1 = (X1 * Z2 ** 2) % self.P
        U2 = (X2 * Z1 ** 2) % self.P
        S1 = (Y1 * Z2 ** 3) % self.P
        S2 = (Y2 * Z1 ** 3) % self.P
        if U1 == U2:
            if S1 != S2:
                return POINT_AT_INFINITY
            else:
                return self.double()
        H = U2 - U1
        R = S2 - S1
        X3 = (R ** 2 - H ** 3 - 2 * U1 * H ** 2) % self.P
        Y3 = (R * (U1 * H ** 2 - X3) - S1 * H ** 3) % self.P
        Z3 = H * Z1 * Z2
        return JacobianPoint(X3, Y3, Z3)

    def __mul__(self, S):
        X1, Y1, Z1 = self.X, self.Y, self.Z

        if Y1 == 0 or self.P == 0:
            return JacobianPoint(0, 0, 1)
        elif S == 1:
            return JacobianPoint(X1, Y1, Z1)
        elif S < 0 or S >= self.N:
            return self * S % self.N
        elif (S % 2) == 0:
            point = AffinePoint(*self.G).to_jacobian() * (S//2)
            return point.double()
        elif (S % 2) == 1:
            point = AffinePoint(*self.G).to_jacobian() * (S//2) + AffinePoint(*self.G).to_jacobian()
            return point.double()

    def __repr__(self):
        return "<JacobianPoint (%s, %s, %s)>" % (self.X, self.Y, self.Z)

    def __str__(self):
        return '(%32x, %32x)' % (self.X, self.Y)

    def double(self):
        """
        Doubles this point.

        Returns:
            JacobianPoint: The point corresponding to `2 * self`.
        """
        X1, Y1, Z1 = self.X, self.Y, self.Z

        if Y1 == 0:
            return POINT_AT_INFINITY
        S = (4 * X1 * Y1 ** 2) % self.P
        M = (3 * X1 ** 2 + self.a * Z1 ** 4) % self.P
        X3 = (M ** 2 - 2 * S) % self.P
        Y3 = (M * (S - X3) - 8 * Y1 ** 4) % self.P
        Z3 = (2 * Y1 * Z1) % self.P
        return JacobianPoint(X3, Y3, Z3)

    def to_affine(self):
        """
        Converts this point to an affine representation.

        Returns:
            AffinePoint: The affine reprsentation.
        """
        X, Y, Z = self.x, self.y, self.inverse(self.z)
        return ((X * Z ** 2) % P, (Y * Z ** 3) % P)

class AffinePoint(secp256k1):
    """
    Provides an affine representation of a point on an elliptic curve. It has
    the standard addition and scalar multiplication operations between two
    points as overloaded '+' and '*' operators.

    Args:
        X (int): X component of the point.
        Y (int): Y component of the point.

    Returns:
        AffinePoint: The point formed by (X, Y).
    """

    def __init__(self, X, Y, infinity=False):
        super().__init__()
        self.X = X
        self.Y = Y
        self.infinity = infinity

    def __add__(self, other):
        X1, Y1 = self.X, self.Y
        X2, Y2 = other.X, other.Y

        if self.infinity:
            return other
        elif other.infinity:
            return self
        elif self == other:
            return self.double()

        if (X1 == X2) and ((Y1 != Y2) or (Y1 == 0 and Y2 ==0)):
            return AffinePoint(0, 0, True)

        S = self.slope(other)
        X3 = (S ** 2 - X1 - X2) % self.P
        Y3 = (S * (X1 - X3) - Y1) % self.P

        return AffinePoint(X3, Y3)

    def __eq__(self, other):
        if not isinstance(other, AffinePoint):
            return False
        return self.X == other.X and self.X == other.Y

    def __ne__(self, other):
        return not (self == other)

    def __mul__(self, other):
        """
        Implements the scalar multiplication via the Montgomery ladder tech-
        nique.
        """
        r0 = AffinePoint(0, 0, True)
        r = [r0, self]

        for i in reversed(range(other.bit_length())):
            di = (other >> i) & 0x1
            r[(di + 1) % 2] = r[0] + r[1]
            r[di] = r[di].double()

        return r[0]

    def __repr__(self):
        return '<AffinePoint (%s, %s)>' % (self.X, self.Y)

    def __str__(self):
        return 'O' if self.infinity else '(%32x, %32x)' % (self.X, self.Y)

    def __sub__(self, other):
        return self + AffinePoint(other.X, self.P - other.Y)

    def double(self):
        """
        Doubles this point.

        Returns:
            AffinePoint: The point corresponding to `2 * self`.
        """
        X1, Y1, a, P = self.X, self.Y, self.a, self.P

        if self.infinity:
            return self

        S = ((3 * X1 ** 2 + a) * self.inverse(2 * Y1)) % P
        X2 = (S ** 2 - (2 * X1)) % P
        Y2 = (S * (X1 - X2) - Y1) % P
        return AffinePoint(X2, Y2)

    def slope(self, other):
        """
        Determines the slope between this point and another point.

        Args:
            other (AffinePoint): The second point.

        Returns:
            int: Slope between self and other.
        """
        X1, Y1, X2, Y2 = self.X, self.Y, other.X, other.Y
        Y3 = Y1 - Y2
        X3 = X1 - X2
        return (Y3 * self.inverse(X3)) % self.P

    def to_jacobian(self):
        """
        Converts this point to a Jacobian representation.

        Returns:
            JacobianPoint: The Jacobian representation.
        """
        if not self:
            return JacobianPoint(X=0, Y=0, Z=0)
        return JacobianPoint(X=self.X, Y=self.Y, Z=1)
