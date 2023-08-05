"""Iterators that wrap iterators for yter"""

import itertools


def call(y, *args, **kwargs):
    """Iterator that works with mixed callable types.

    Iterate over all the values from the input iterator. If one of the values
    is a callable object it will be called and its return will be the value
    instead.

    The `args` and `kwargs` arguments will be passed to any callable values
    in the iterator.

    """
    vals = []
    _callable = callable  # Local cache
    for val in y:
        if _callable(val):
            val = val(*args, **kwargs)
        yield val


def percent(y, percent):
    """Iterator that skips a percentage of values.

    The `percent` is a floating point value between 0.0 and 1.0. If the value
    is larger than 1.0 it will be the same as 1.0. If the value is less than
    or equal to 0.0 no values will be iterated.

    As long as the `percent` is greater than 0.0 the first value
    will always be iterated.

    """
    if percent <= 0.0:
        return iter(())
    elif percent >= 1.0:
        return y

    def genpercent(y, percent):
        nom, denom = float(percent).as_integer_ratio()
        count = denom
        for val in y:
            if count >= denom:
                yield val
                count += nom
                count -= denom
            else:
                count += nom
    return genpercent(y, percent)


def flat(y):
    """Iterator of values from a iterable of iterators.

    This removes a level of nesting. When given a list of lists this will
    iterate the values from those children lists.

    This is the same as `itertools.chain.from_iterable` with a more memorable
    name.

    This will invert the results of the `chunk` iterator.
    """
    return itertools.chain.from_iterable(y)


def chunk(y, size):
    """Iterator of lists with a fixed size from iterable.

    Group the values from the iterable into lists up to a given size.
    The final list generated can be smaller than the given size.

    """
    y = iter(y)
    _len = len
    while 1:
        values = list(itertools.islice(y, size))
        l = _len(values)
        yield values
        if l < size:
            break

