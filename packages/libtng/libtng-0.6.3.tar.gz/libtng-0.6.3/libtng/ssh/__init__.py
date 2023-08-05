import os
import errno
import stat
import getpass

from Crypto.PublicKey import RSA

from libtng.exceptions import ResourceDoesNotExist,\
    SuspiciousOperation

__all__ = [
    'generate_keypair',
    'get_publickey',
    'Keypair',
    'IdentityRSA',
    'IdentityDoesNotExist'
]



class IdentityDoesNotExist(ResourceDoesNotExist):
    pass


class InsecureFilePermissions(SuspiciousOperation):
    pass



class IdentityRSA(object):
    """
    Represents a RSA private key.
    """
    encryption_type = 'RSA'

    @classmethod
    def fromfilepath(cls, src):
        """
        Return a new :class:`IdentityRSA` instance using
        the specified filepath `src`.
        """
        try:
            mask = oct(os.stat(src)[stat.ST_MODE])[-3:]
            if not (mask == '600'):
                raise InsecureFilePermissions(
                    "Insecure permissions bitmask on {0}: {1}"\
                        .format(src, mask))
            return cls(open(src).read(), src=src)
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise
            raise IdentityDoesNotExist(*e.args)

    @classmethod
    def generate(cls, dst, passphrase=None, bits=2048):
        """
        Generate an RSA private key and return a :class:`IdentityRSA`
        representing it.

        :param dst:
            the destination to save the key.
        :param passphrase:
            the passphrase, if the private key needs one.
        """
        key = RSA.generate(bits)
        with open(dst, 'wb') as f:
            f.write(key.exportKey())
        os.chmod(dst, stat.S_IRUSR | stat.S_IWUSR)
        return cls.fromfilepath(dst)

    @classmethod
    def temporary(self, bits=2048):
        """
        Generate a temporary RSA private key.
        """
        return cls(RSA.generate(bits).exportKey(), temporary=True)

    @property
    def filepath(self):
        return self.__filepath

    def __init__(self, content, src=None, temporary=False):
        if not (bool(src) ^ bool(temporary)):
            raise TypeError("Specify either `src` or `temporary`, and not both.")
        self.__content = content
        self.__filepath = src
        self.__fp = None
        if temporary:
            self.__fp = tempfile.NamedTemporaryFile()
            self.__fp.write(self.__content)
            self.__fp.seek(0)
            os.chmod(self.__fp.name, stat.S_IRUSR | stat.S_IWUSR)
        self.__public = None

    def generate_public(self, passphrase=None, format='OpenSSH'):
        """
        Generate a public key.

        :param passphrase:
            the passphrase, if the identity has one.
        :param format:
            specifies the output format. Default is ``'OpenSSH'``.
        :returns:
            a string holding the public key.
        """
        if self.__public is None:
            key = RSA.importKey(self.__content,
                passphrase=passphrase)
            self.__public = key.publickey().exportKey('OpenSSH')
        return self.__public

    def is_temporary(self):
        """
        Return a :class:`bool` indicating if the private key
        is temporary and will be deleted by the garbage
        collector.
        """
        return self.__fp is not None

    def __repr__(self):
        return "Identity{0}(user='{1}', temporary={2})"\
            .format(self.encryption_type, getpass.getuser(),
                'True' if self.is_temporary() else 'False')


class Keypair(tuple):
    """
    A Value Object representing an OpenSSH private/public
    keypair.

    :ivar private:
        a :class:`str` containing the private key.

    :ivar public:
        a :class:`str` containing the public key.
    """

    @property
    def private(self):
        return self[0]

    @property
    def public(self):
        return self[1]

    @classmethod
    def generate(self, bits=2048):
        """
        Generate an OpenSSH private/public keypair.

        :param bits:
            the bitlength of the key; default is 2048.
        :returns:
            a :class:`Keypair` containing `private`, `public`
            keys.
        """
        return cls(*generate_keypair(bits=bits))

    @classmethod
    def fromprivate(cls, private, passphrase=None):
        """
        Return a new :class:`Keypair` instance using a
        RSA private key.

        :param private:
            a :class:`str` containing the private key.
        :param passphrase:
            the passphrase, if the private key has one.
        :returns:
            :class:`Keypair`.
        """
        key = RSA.importKey(private, passphrase=passphrase)
        return cls(private, key.publickey().exportKey('OpenSSH'))

    def __new__(cls, private, public):
        return tuple.__new__(cls, [private, public])


def generate_keypair(bits=2048):
    """
    Generate an OpenSSH private/public keypair.

    :param bits:
        the bitlength of the key; default is 2048.
    :returns:
        a :class:`tuple` containing `private`, `public`
        keys.
    """
    key = RSA.generate(2048)
    return (
        key.exportKey(),
        key.publickey().exportKey('OpenSSH')
    )


def get_publickey(private_key_file='~/.ssh/id_rsa', passphrase=None):
    """
    Generate an OpenSSH public key.

    :param private_key_file:
        specifies the private key file; by default the private
        key (id_rsa) of the user running the current interpreter.
    :param passphrase:
        the passphrase, if the private key has one.
    :returns:
        a :class:`str` holding the public key.
    """
    private_key_file = os.path.expanduser(private_key_file)
    with open(private_key_file, "r") as f:
        key = RSA.importKey(f, passphrase=passphrase)
    return key.publickey().exportKey('OpenSSH')