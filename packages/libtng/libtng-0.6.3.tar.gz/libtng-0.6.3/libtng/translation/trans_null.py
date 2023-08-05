# These are versions of the functions in django.utils.translation.trans_real
# that don't actually do anything. This is purely for performance, so that
# const.USE_I18N = False can use this module rather than trans_real.py.
from libtng.encoding import force_text
from libtng.safestring import mark_safe, SafeData
from libtng import const


def ngettext(singular, plural, number):
    if number == 1: return singular
    return plural
ngettext_lazy = ngettext


def ungettext(singular, plural, number):
    return force_text(ngettext(singular, plural, number))


def pgettext(context, message):
    return ugettext(message)


def npgettext(context, singular, plural, number):
    return ungettext(singular, plural, number)


activate = lambda x: None
deactivate = deactivate_all = lambda: None
get_language = lambda: const.LANGUAGE_CODE
get_language_bidi = lambda: const.LANGUAGE_CODE in const.LANGUAGES_BIDI
check_for_language = lambda x: True


# date formats shouldn't be used using gettext anymore. This
# is kept for backward compatibility
TECHNICAL_ID_MAP = {
    "DATE_WITH_TIME_FULL": const.DATETIME_FORMAT,
    "DATE_FORMAT": const.DATE_FORMAT,
    "DATETIME_FORMAT": const.DATETIME_FORMAT,
    "TIME_FORMAT": const.TIME_FORMAT,
    "YEAR_MONTH_FORMAT": const.YEAR_MONTH_FORMAT,
    "MONTH_DAY_FORMAT": const.MONTH_DAY_FORMAT,
}


def gettext(message):
    result = TECHNICAL_ID_MAP.get(message, message)
    if isinstance(message, SafeData):
        return mark_safe(result)
    return result


def ugettext(message):
    return force_text(gettext(message))

gettext_noop = gettext_lazy = _ = gettext


def to_locale(language):
    p = language.find('-')
    if p >= 0:
        return language[:p].lower()+'_'+language[p+1:].upper()
    else:
        return language.lower()


def get_language_from_request(request, check_path=False):
    return const.DEFAULT_LANGUAGE


def get_language_from_path(request, supported=None):
    return None

