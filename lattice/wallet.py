# -*- coding: utf-8 -*-

"""
This module allows the creation of wallets for various native cryptos.
"""

from __future__ import print_function
import hashlib
import binascii


# Elliptic curve parameters (secp256k1)
# See https://en.bitcoin.it/wiki/Secp256k1
P = 2**256 - 2**32 - 2**9 - 2**8 - 2**7 - 2**6 - 2**4 - 1
A = 0
B = 7
Gx = 55066263022277343669578718895168534326250603453777594175500187360389116729240
Gy = 32670510020758816978083085130507043184471273380659243275938904335757337482424
G = (Gx, Gy)
N = 115792089237316195423570985008687907852837564279074904382605163141518161494337

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
    private_key_int = int(private_key, 16)
    if private_key_int >= N:
        raise Exception('Invalid private key.')

    # Converting (x, y) to the Jacobian coordinates (x, y, z)
    G_jacobian_coords = (G[0], G[1], 1)

    def jacobian_double(point):
        x, y, z = point
        if not y:
            return (0, 0, 0)
        ysq = (y ** 2) % P
        S = (4 * x * ysq) % P
        M = (3 * x ** 2 + A * z ** 4) % P
        x_prime = (M ** 2 - 2 * S) % P
        y_prime = (M * (S - x_prime) - 8 * ysq ** 2) % P
        z_prime = (2 * y * z) % P
        return (x_prime, y_prime, z_prime)

    def jacobian_add(p, q):
        if not p[1]:
            return q
        if not q[1]:
            return p
        U1 = (p[0] * q[2] ** 2) % P
        U2 = (q[0] * p[2] ** 2) % P
        S1 = (p[1] * q[2] ** 3) % P
        S2 = (q[1] * p[2] ** 3) % P
        if U1 == U2:
            if S1 != S2:
                return (0, 0, 1)
            return jacobian_double(p)
        H = U2 - U1
        R = S2 - S1
        H2 = (H * H) % P
        H3 = (H * H2) % P
        U1H2 = (U1 * H2) % P
        nx = (R ** 2 - H3 - 2 * U1H2) % P
        ny = (R * (U1H2 - nx) - S1 * H3) % P
        nz = (H * p[2] * q[2]) % P
        return (nx, ny, nz)

    def jacobian_multiply(a, n):
        if a[1] == 0 or n == 0:
            return (0, 0, 1)
        if n == 1:
            return a
        if n < 0 or n >= N:
            return jacobian_multiply(a, n % N)
        if (n % 2) == 0:
            return jacobian_double(jacobian_multiply(a, n//2))
        if (n % 2) == 1:
            return jacobian_add(jacobian_double(jacobian_multiply(a, n//2)), a)

    def inv(a, n):
        if a == 0:
            return 0
        lm, hm = 1, 0
        low, high = a % n, n
        while low > 1:
            r = high//low
            nm, new = hm-lm*r, high-low*r
            lm, low, hm, high = nm, new, lm, low
        return lm % n

    def from_jacobian(p):
        z = inv(p[2], P)
        return ((p[0] * z**2) % P, (p[1] * z**3) % P)

    def encode(val, base, minlen=0):
        base, minlen = int(base), int(minlen)
        code_string = '0123456789abcdef'
        result_bytes = bytes()
        while val > 0:
            curcode = code_string[val % base]
            result_bytes = bytes([ord(curcode)]) + result_bytes
            val //= base

        pad_size = minlen - len(result_bytes)

        padding_element = b'\x00' if base == 256 else b'1' \
            if base == 58 else b'0'
        if (pad_size > 0):
            result_bytes = padding_element*pad_size + result_bytes

        result_string = ''.join([chr(y) for y in result_bytes])
        result = result_bytes if base == 256 else result_string

        return result

    def encode_public_key(pub):
        return '04' + encode(pub[0], 16, 64) + encode(pub[1], 16, 64)

    public_key = encode_public_key(
        from_jacobian(
            jacobian_multiply(
                G_jacobian_coords, private_key_int
            )
        )
    )
    print(public_key)

class JacobianPoint(object):
    """
    Defines a Jacobian coordinate system point and operations that can be
    performed.
    https://en.wikibooks.org/wiki/Cryptography/Prime_Curve/Jacobian_Coordinates
    """

    def __init__(self, x, y, z, curve):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        raise NotImplementedError()

    def __repr__(self):
        return "<JacobianPoint (%s, %s, %s)>" %(self.x, self.y, self.z)

    def to_affine(self):
        raise NotImplementedError()

    def double(self):
        raise NotImplementedError()

class AffinePoint(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self):
        raise NotImplementedError()

    def __eq__(self, other):
        if not isinstance(other, AffinePoint):
            return False
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not (self == other)

    def __mul__(self):
        raise NotImplementedError()

    def __repr__(self):
        return "<AffinePoint (%s, %s)>" % (self.x, self.y)

    def double(self):
        raise NotImplementedError()

    def to_jacobian(self):
        if not self:
            return JacobianPoint(x=0, y=0, z=0)
        return JacobianPoint(x=self.x, y=self.y, z=1)
