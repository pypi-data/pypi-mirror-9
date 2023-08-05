import sys
import copy
import datetime
import collections
import pytz
from dateutil import parser


PYTHON_MAJOR_VERSION = int(sys.version_info[0])


def update_dict(d, u):
    """update dict-instance recursive.
    """
    if PYTHON_MAJOR_VERSION == 3:
        it_ = u.items
    else:
        it_ = u.iteritems
    d_ = copy.deepcopy(d)
    for k, v in it_():
        if isinstance(v, collections.Mapping):
            r = update_dict(d_.get(k, {}), v)
            d_[k] = r
        else:
            d_[k] = u[k]
    return d_


def strptime(date_string):
    """wrapper to parse datetime-string for Twitter-API
    """
    try:
        datetime_data = parser.parse(date_string)
    except:
        datetime_data = datetime.datetime.strptime(
            date_string,
            '%a %b %d %H:%M:%S +0000 %Y'
        )
        datetime_data = pytz.utc.localize(datetime_data)
    return datetime_data
