#!/usr/bin/env python
import unittest
import datetime

import base
from libtng.http.utils import signed_authorization_header
from libtng.http.utils import parse_authorization_header
from libtng.hashers.signing import check_message
from libtng.hashers.signing import sign_message


PRIVATE_KEY1 = 'f15404d7-ae44-4af1-bcd0-d93037ead79c'
PRIVATE_KEY2 = 'f15404d7ae444af1bcd0d93037ead79c'


class SigningTestCase(unittest.TestCase):
    """
    Signing must ignore the dashes in private keys.
    """

    def test_dashes_against_non_dashes_check(self):
        header = signed_authorization_header('Phalanx', ['username', 'foo'],
            PRIVATE_KEY1, '')
        protocol, params = parse_authorization_header(header)
        self.assertTrue(check_message(params['signature'], PRIVATE_KEY2, '',
            params['timestamp']))

    def test_dashes_against_non_dashes_eq(self):
        dt = datetime.datetime.utcnow()
        self.assertEqual(
            sign_message(PRIVATE_KEY1, '', timestamp=dt),
            sign_message(PRIVATE_KEY2, '', timestamp=dt)
        )


if __name__ == '__main__':
    unittest.main()