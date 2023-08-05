"""Functions that make useful keys"""

import re


def formatter(fmt, **kwargs):
    """Create a function that formats given values into strings.

    Additional keywoard arguments can be given that will also be passed to
    the format function.

    The values passed to the formatter will be given as the first argument
    to format, which is referenecd as {0}.

    """
    def formatted(val):
        return fmt.format(val, **kwargs)
    return formatted


_numberRegex = None

def numeric(value):
    """Split a string into string and integer sections.

    A string will be a tuple containing sections that are strings
    and integers. The numeric parts of the string will be converted
    into integers.

    This is a convenient way to sort string containing numbers that
    are not padded.

    Negative numbers will also be converted if precedded by a single
    minus sign.

    """
    global _numberRegex

    if not value:
        return ()

    if not _numberRegex:
        _numberRegex = re.compile("(-?\d+)")
    parts = _numberRegex.split(value)
    # Values that start with digits will get a leading empty string
    if value[0].isdigit():
        parts = parts[1:]
    if value[-1].isdigit():
        parts.pop()

    converted = tuple(int(p) if p[-1].isdigit() else p
                for p in parts)
    return converted
