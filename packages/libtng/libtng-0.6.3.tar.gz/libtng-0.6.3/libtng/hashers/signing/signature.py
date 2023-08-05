from hashlib import sha512
import datetime


from libtng.hashers.signing.utils import check_message
from libtng.hashers.signing.utils import sign_message
from libtng.hashers.signing.utils import get_message_digest


class Signature(object):
    """
    Represents the signature of a message.
    """

    @property
    def signature(self):
        return self._signature

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def digest(self):
        return self._digest

    @classmethod
    def sign(cls, private_key, message):
        args = sign_message(private_key, message, digestmod=sha512, timestamp=None)
        return cls(*args)

    @classmethod
    def from_message(cls, signature, timestamp, message,
        digest=get_message_digest):
        """
        Initialize a new :class:`Signature` instance from a
        message.

        Args:
            signature (str): the signature of a message.
            timestamp (datetime.datetime): specifies the date and time a
                signature was generated.
            message (str): the message to be signed.

        Kwargs:
            digest (types.FunctionType): a callabje that returns the
                digest of `message`.

        Returns:
            Signature: the signature of the message.
        """
        return cls(signature, timestamp, digest(message))

    def __init__(self, signature, timestamp, digest):
        """
        Initialize a new :class:`Signature` instance.

        Args:
            signature (str): the signature of a message.
            timestamp (datetime.datetime): specifies the date and time a
                signature was generated.
            digest (str): the message digest.
        """
        if not isinstance(timestamp, datetime.datetime):
            timestamp = dateutil.parser.parse(timestamp)
        self._signature = signature
        self._timestamp = timestamp
        self._digest = digest

    def verify(self, private_key):
        """Verifies the message.

        Args:
            private_key (str): the private key that was used to sign
                a message.

        Returns:
            bool: indicates if the signature is valid.
        """
        return check_message(self._signature, private_key,
            self._digest, self._timestamp)

    def __iter__(self):
        return iter([self._signature, self._timestamp, self._digest])

    def __repr__(self):
        return "Signature(signature='{0}', timestamp='{1}', digest='{2}')"\
            .format(self._signature, str(self._timestamp), self._digest)
