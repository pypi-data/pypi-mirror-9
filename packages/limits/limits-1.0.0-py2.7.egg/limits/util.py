"""

"""
import re
import sys

from .limits import GRANULARITIES


EXPR = re.compile(
    r"\s*([0-9]+)\s*(/|\s*per\s*)\s*([0-9]+)*\s*(hour|minute|second|day|month|year)[s]*",
    re.IGNORECASE
)

def get_dependency(dep):
    """
    safe function to import a module programmatically
    :return: module or None (if not importable)
    """
    try:
        __import__(dep)
        return sys.modules[dep]
    except ImportError: # pragma: no cover
        return None


def parse_many(limit_string):
    """

    :param limit_string:
    :raise ValueError:
    """
    if not EXPR.match(limit_string):
        raise ValueError("couldn't parse rate limit string '%s'" % limit_string)
    for amount, _, multiples, granularity_string in  EXPR.findall(limit_string):
        granularity = granularity_from_string(granularity_string)
        yield granularity(amount, multiples)

def parse(limit_string):
    """

    :param limit_string:
    :return:
    """
    return list(parse_many(limit_string))[0]


def granularity_from_string(granularity_string):
    """

    :param granularity_string:
    :return: a :class:`flask_ratelimit.limits.Item`
    :raise ValueError:
    """
    for granularity in GRANULARITIES:
        if granularity.check_granularity_string(granularity_string):
            return granularity
    raise ValueError("no granularity matched for %s" % granularity_string)

