from os.path import join
import re


def str_to_pattern(value):
    p = re.escape(value)\
            .replace('\*','.*')\
            .replace('\.','.')

    return re.compile("^{0}$".format(p))


#: Matches against an Internet Media Type.
mimetype = re.compile("^(application|audio|image|video|message|model|multipart|text)/.*$")


#: Matches against a hostname per RFC 1123 See
#: http://www.dns-sd.org/TrailingDotsInDomainNames.html
rfc1123 = re.compile("^([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])\.?)*$")

#: Matches againt an IPv4 address.
inet4 = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")

#: Matches against a hostname per RFC 1123
hostname = rfc1123

#: Matches against a valid subdomain.
subdomain = re.compile("^(?:[A-Za-z0-9][A-Za-z0-9\-]{0,61}[A-Za-z0-9]|[A-Za-z0-9])$")

#: Matches a string containing an UUID of 32 characters or
#: 36 characters with dashes.
uuid = re.compile('([0-9a-f]{32}|[0-9a-f\-]{36})\Z', re.I)


def camel2upper(value):
    """
    Convert a *CamelCase* string to *UPPER_CASE*.
    """
    value = re.sub('(?!^)[A-Z]', lambda x: '_' + x.group(0), value)
    return value.upper()


def underscore2camel(value):
    return ''.join([x[0].upper() + x[1:] for x in value.split('_')])