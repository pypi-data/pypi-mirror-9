



class Argument(object):
    """Represents an argument to a subparser."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_to_subparser(self, subparser):
        subparser.add_argument(*self.args, **self.kwargs)

    def get_args(self):
        return self.args

    def get_kwargs(self):
        return self.kwargs