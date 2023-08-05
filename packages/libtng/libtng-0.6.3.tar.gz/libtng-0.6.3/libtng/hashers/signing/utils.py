from hashlib import sha512, sha1
import hmac
import binascii
import datetime
import re
import struct

from libtng import timezone


#: The maximum age of a message, in seconds.
MESSAGE_MAX_AGE = 300


class MessageExpired(Exception):
    """Indicates that a signed message has expired."""


def _sign_payload(private_key, payload, timestamp, digestmod=None):
    private_key = (private_key or '').replace('-','')
    digestmod = digestmod or sha512
    signature = hmac.new(private_key, (payload or '') + str(timestamp or ''), digestmod)

    # The byte order is probably relevant, but we haven't
    # run into any problems yet. I like a nice numeral-only
    # signature because that just looks more 1337 than a
    # stupid base64-encoded string.
    return ''.join(map(str, struct.unpack('>QQQQQQQQ', signature.digest())))


def _generate_digest(payload):
    return sha1(payload).hexdigest()


def get_message_digest(message):
    return sha1(message).hexdigest()


def sign_message(private_key, payload, digestmod=sha512, timestamp=None):
    """
    Generate a signature to authenticate a request.

    Args:
        private_key: a string containing the private key.
        payload: a string containing the request body.

    Returns:
        tuple: containing a :class:`str` and a
            :class:`datetime.datetime`, holding the
            authentication signature and the request
            timestamp.
    """
    digest = _generate_digest(payload)
    timestamp = timestamp or datetime.datetime.utcnow()
    signature = _sign_payload(private_key, digest, timestamp,
        digestmod=digestmod)
    return signature, timestamp, digest


def check_message(signature, private_key, digest, timestamp, digestmod=sha512, max_age=None):
    """Validates an authentication signature.

    Args:
        private_key: a string containing the private key.
        digest: a string containing the message digest.
        timestamp: a :class:`datetime.datetime` instance
            representing the timestamp of the request.

    Returns:
        bool
    """
    # We should validate the timestamp to prevent replay attacks
    # against signed messages.
    max_age = max_age or datetime.timedelta(seconds=MESSAGE_MAX_AGE)
    if (timestamp + max_age) < datetime.datetime.utcnow():
        is_valid = False
    else:
        local_signature = _sign_payload(private_key, digest, timestamp,
        digestmod=digestmod)
        # Use SHA-1 hashes to prevent timing attacks.
        is_valid = sha1(signature).hexdigest() == sha1(local_signature).hexdigest()
    return is_valid
