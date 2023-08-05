

class Collection(list):

    @property
    def cls(self):
        return type(self)

    def map(self, func, *others):
        """
        Return a list of the results of applying the function to the items of
        the argument sequence(s).  If more than one sequence is given, the
        function is called with an argument list consisting of the
        corresponding item of each sequence, substituting None for missing
        values when not all sequences have the same length.  If the function
        is None, return a list of the items of the sequence (or a list of
        tuples if more than one sequence).
        """
        return self.cls(map(func, self, *others))

    def reduce(self, func, initial=None):
        """
        Apply a function of two arguments cumulatively to the items of
        a sequence, from left to right, so as to reduce the sequence to
        a single value. For example, reduce(lambda x, y: x+y, [1, 2, 3, 4,
        5]) calculates ((((1+2)+3)+4)+5).  If initial is present, it is
        placed before the items of the sequence in the calculation, and
        serves as a default when the sequence is empty.
        """
        return reduce(func, self, initial)

    def filter(self, func):
        """
        Return those items of sequence for which function(item) is true.
        If function is None, return the items that are true.
        """
        return self.cls(filter(func, self))

    def join(self, sep):
        """
        Return a string which is the concatenation of the strings in the
        iterable.  The separator between elements is S.
        """
        return sep.join(self)
