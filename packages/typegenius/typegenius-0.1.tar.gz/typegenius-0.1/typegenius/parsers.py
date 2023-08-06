import locale
from datetime import datetime

env = locale.localeconv()
dc = env['decimal_point']
ts = env['thousands_sep']


def is_float(val, out_res=None):
    if out_res is None:
        out_res = []
    if isinstance(val, float):
        out_res.append(val)
        return True
    elif dc in str(val) and str(val).replace(dc, '').replace(ts, '').isdigit():
        out_res.append(float(val))
        return True
    else:
        return False


def is_int(val, out_res=None):
    if out_res is None:
        out_res = []
    if isinstance(val, int):
        out_res.append(val)
        return True
    elif str(val).replace(ts, '').isdigit():
        out_res.append(int(val))
        return True
    else:
        return False


def is_bool(val, out_res=None):
    if out_res is None:
        out_res = []
    if isinstance(val, bool):
        out_res.append(val)
        return True
    elif str(val).lower() in ['true', 'false']:
        out_res.append(bool(val))
        return True
    else:
        return False


def is_date(val, out_res=None):
    if out_res is None:
        out_res = []
    if isinstance(val, datetime):
        out_res.append(val)
        return True
    # TODO: Add support for parsing different datetime formats
    else:
        return False


def get(val):
    out_res = []
    if val is None:
        return None
    elif is_float(val, out_res):
        return out_res[0]
    elif is_int(val, out_res):
        return out_res[0]
    elif is_bool(val, out_res):
        return out_res[0]
    elif is_date(val, out_res):
        return out_res[0]
    else:
        return str(val)