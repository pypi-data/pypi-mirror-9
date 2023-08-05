from libtng.sil.index import LanguageIndexCollection
from libtng.sil.index import LanguageIndex
from libtng.sil.language import LanguageCollection
from libtng.sil.language import Language



def get_languages():
    """
    Return a list of tuples identifying ISO 639-3 elements.
    """
    return map(lambda x: x.as_tuple(), LanguageCollection.fromsil())


def get_indexes():
    """
    Return a list of tuples identifying ISO 639-3 element
    indexes.
    """
    return map(lambda x: x.as_tuple(), LanguageIndexCollection.fromsil())