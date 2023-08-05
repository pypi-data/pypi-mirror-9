# -*- coding: utf-8 -*-

__version__ = "0.1.5"

from collections import namedtuple, Counter
from uuid import uuid4


def name(prefix="istruct"):
    return "{prefix}_{uuid}".format(prefix=prefix,
                                    uuid=str(uuid4()).replace("-", ""))


def merge_tuples(*tuples):
    return ", ".join(item for t in tuples for item in t)


def merge_dicts(*dicts):
    return {k: v for d in dicts for k, v in d.items()}


def validate(f):
    """Do simple validation checks on positional and keyword arguments.
    """
    def _validate(*args, **kwargs):
        # field cannot be repeated
        repeated = sorted([k for k, v in Counter(args).items() if v > 1])
        if repeated:
            raise ValueError("Each field cannot be present more than once: "
                             "%s" % (", ".join("'%s'" % f for f in repeated),))

        # field cannot be both required and optional
        both = set(args).intersection(set(kwargs.keys()))
        if both:
            raise ValueError("Each field must be either required or optional, "
                             "not both: "
                             "%s" % ", ".join("'%s'" % f for f in both))

        return f(*args, **kwargs)

    return _validate


@validate
def istruct(*args, **kwargs):
    """Implement an immutable struct on top of `collections.namedtuple`.
    """
    def _istruct(*positional, **attrs):
        # no positional arguments are allowed
        if positional:
            raise TypeError("No positional arguments are allowed in istruct "
                            "(%d found)" % (len(positional),))

        nt = namedtuple(__name__,
                        merge_tuples(args, tuple(kwargs.keys())))
        return nt(**merge_dicts(kwargs, attrs))

    return _istruct
