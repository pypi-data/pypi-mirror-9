# -*- coding: utf-8 -*-
# Part of the scorify package
# Copyright 2014 Board of Regents of the University of Wisconsin System

"""
Aggregators are functions that consense sets of numbers into single ones.
They're used by measure directives.
"""

import math
import re

expr_re = re.compile(r"""
    (\w+)  # Function name
    \(
    ([^)]+) # Yup, you can put anything in the parens
    \)
""", re.VERBOSE | re.IGNORECASE)


def parse_expr(expr):
    fx_map = {
        'sum': ag_sum,
        'mean': ag_mean,
        'join': ag_join,
    }
    try:
        fx_name, measure_names = expr_re.match(expr).groups()
        fx_name = fx_name.lower()
        measure_names = [m.strip() for m in measure_names.split(",")]
    except AttributeError as err:
        raise AggregatorError("I don't understand {0!r}: {1}".format(expr, err))
    try:
        fx = fx_map[fx_name]
    except KeyError:
        raise AggregatorError("I don't know {0}".format(fx_name))
    return (fx_name, fx, measure_names)


# sum is a reserved word in python because goddammt
def ag_sum(values):
    return math.fsum([float(v) for v in values])


def ag_mean(values):
    return ag_sum(values)/float(len(values))


def ag_join(values):
    # Filters out empty values.
    values = [str(v) for v in values if len(str(v).strip()) > 0]
    return '|'.join([str(v) for v in values])


class AggregatorError(ValueError):
    pass
