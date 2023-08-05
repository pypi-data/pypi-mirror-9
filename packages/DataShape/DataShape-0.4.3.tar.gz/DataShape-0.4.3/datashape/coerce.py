from __future__ import print_function, division, absolute_import

import numpy as np
from dateutil.parser import parse as dateparse
from datetime import datetime, date
from .dispatch import dispatch
from time import strptime

from .coretypes import (int32, int64, float64, bool_, complex128, datetime_,
                        Option, var, from_numpy, Tuple, null,
                        Record, string, Null, DataShape, real, date_, time_, Mono)
from .py2help import _strtypes
from .internal_utils import _toposort, groupby

@dispatch(object, type(string))
def coerce(o, s):
    return str(o)


@dispatch(_strtypes, type(datetime))
def coerce(s, _):
    return dateparse(s)


@dispatch(_strtypes, type(date_))
def coerce(s, _):
    return coerce(s, datetime_).date()


@dispatch(_strtypes, type(time_))
def coerce(s, _):
    return coerce(s, datetime_).time()
