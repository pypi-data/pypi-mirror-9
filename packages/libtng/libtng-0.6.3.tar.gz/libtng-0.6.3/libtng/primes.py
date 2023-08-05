


def primes(n):
    """
    Returns the prime factors of the specified number.

    Args:
        x: an unsigned integer.

    Returns:
        tuple
    """
    primfac = set()
    d = 2
    while d*d <= n:
        while (n % d) == 0:
            primfac.add(d)
            n /= d
        d += 1
    if n > 1:
       primfac.add(n)
    return tuple(sorted(primfac))