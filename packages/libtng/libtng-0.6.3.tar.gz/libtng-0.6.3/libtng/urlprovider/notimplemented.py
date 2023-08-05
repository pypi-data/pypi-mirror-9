from libtng.urlprovider.iurlprovider import IUrlProvider


class MissingLibraryUrlProvider(IUrlProvider):
    module_name = None

    @classmethod
    def create_class(cls, module_name, class_name):
        return type(class_name, (cls,), {'module_name': module_name})

    def __init__(self, *args, **kwargs):
        pass

    def add(self, *args, **kwargs):
        raise NotImplementedError(
            "The `{0}` library is not installed.".format(self.module_name))
