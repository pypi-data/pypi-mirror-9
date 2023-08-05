import unittest

from libtouchngo.hashers.pbkdf2_sha256 import PBKDF2PasswordHasher


class PBKDF2PasswordHasherTestCase(unittest.TestCase):
    password = 'foo'
    salt = 'bar'
    hasher_class = PBKDF2PasswordHasher
    iterations = 1

    def setUp(self):
        self.hasher = self.hasher_class()
        self.encoded = self.hasher.encode(self.password, self.salt, iterations=self.iterations)

    def test_verify(self):
        self.assertTrue(self.hasher.verify(self.password, self.encoded))
