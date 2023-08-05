from libtng.checksum.checksum import Checksum


class Verhoeff(Checksum):
    """
    Create and validate checksums using the Verhoeff algorithm.
    """
    value_type = int
    valid_checksum = 0

    _multiplication_table = (
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
        [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
        [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
        [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
        [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
        [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
        [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
        [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
        [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
        [9, 8, 7, 6, 5, 4, 3, 2, 1, 0])

    _permutation_table = (
        (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
        (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
        (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
        (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
        (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
        (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
        (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
        (7, 0, 4, 6, 9, 1, 3, 2, 5, 8))

    def checksum(self, value):
        """
        Calculate the Verhoeff checksum over the provided
        number `value`. Valid values should have a checksum
        of 0.
        """
        value = tuple(int(n) for n in reversed(str(value)))
        check = 0
        for i, n in enumerate(value):
            check = self._multiplication_table[check][self._permutation_table[i % 8][n]]
        return check

    def check_digit(self, value):
        """
        With the provided number `value`, calculate the extra
        digit that should be appended to make it pass the
        Verhoeff checksum.
        """
        checksum = self.checksum(str(value) + '0')
        return str(self._multiplication_table[checksum].index(0))
