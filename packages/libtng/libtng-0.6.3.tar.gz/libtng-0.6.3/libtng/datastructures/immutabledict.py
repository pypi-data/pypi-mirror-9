


class ImmutableDict(dict):

    def __setitem__(self, key, value):
        raise NotImplementedError("Cannot set item to ImmutableDict")