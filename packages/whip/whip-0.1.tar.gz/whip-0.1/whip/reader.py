"""
Whip reader module.
"""

from .json import loads
from .util import ip_str_to_int

DEFAULT_RANGE_FIELDS = ('begin', 'end')


def iter_json(fp, range_fields=DEFAULT_RANGE_FIELDS):
    """Read a JSON formatted stream of data from a file like object.

    Each line in the input file must contain a valid JSON document. The
    fields specified by `range_fields` should contain IP addresses that
    are used as the beginning and end of the range.

    The input must already be sorted by IP range, and the ranges must
    not overlap.

    This function yields ``(begin, end, doc)`` tuples, where both
    `begin` and `end` are integer representations of the IP addresses
    contained in the document.
    """

    begin_field, end_field = range_fields
    _ip_str_to_int = ip_str_to_int
    _loads = loads

    for line in fp:
        doc = _loads(line)
        yield (
            _ip_str_to_int(doc[begin_field]),
            _ip_str_to_int(doc[end_field]),
            doc,
        )
