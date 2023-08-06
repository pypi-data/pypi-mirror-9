from typegenius import localization, dates, util
from typegenius.dates import DatePart, Month
from datetime import datetime


def is_float(val, out_res=None):
    if out_res is None:
        out_res = []

    if isinstance(val, float):
        out_res.append(val)
        return True

    dc = localization.get_decimal_separator()
    ts = localization.get_thou_separator()

    if dc in str(val) and str(val).replace(dc, '').replace(ts, '').isdigit():
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

    ts = localization.get_thou_separator()

    if str(val).replace(ts, '').isdigit():
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


def is_date_rfc_3339(val, out_res=None):
    """
    Format: 1997-07-16T19:20:30.45+01:00
    Allows the "T" to be replaced by a space (or other character)
    Allows -00:00
    """
    parts = dates.get_descending_parts(val)

    if len(list(p for p in parts if p != DatePart.fraction and parts[p] is None)) > 0:
        return False  # Requires a complete representation of date and time (only fractional seconds are optional)
    if parts[DatePart.fraction] is not None and parts[DatePart.fraction] != '.':
        return False  # Only allows a period character to be used as the decimal point for fractional seconds

    if out_res is None:
        out_res = []

    date = dates.create_date(parts)
    out_res.append(date)

    return True


def is_date_iso_8601(val, out_res=None):
    """
    Format: 1997-07-16T19:20:30.45+01:00
    Allows elements to the right to be omitted
    Does not allow T to be replaced only omitted
    """
    parts = dates.get_descending_parts(val)

    if parts[DatePart.year] is None or parts[DatePart.month] is None or parts[DatePart.month] is None:
        return False  # Requires at least the date
    if parts[DatePart.fraction] is not None and parts[DatePart.fraction] not in ['.', ',']:
        return False  # Allows comma or period for decimal fractions of time elements
    if not parts[DatePart.zone_sign] and parts[DatePart.zone_h] == 0:
        return False  # Does not allow -00:00

    if out_res is None:
        out_res = []

    date = dates.create_date(parts)
    out_res.append(date)

    return True


def is_date_rfc_2822(val, out_res=None):
    """
    Code:       RFC 2822
    Format:     day-name, 2DIGIT month-name 4DIGIT 2DIGIT:2DIGIT:2DIGIT +|-4DIGIT
    Example:    Wed, 05 Oct 2011 22:26:12 -0400
    """
    try:
        lst = util.split(val, [' ', ',', ':'], remove_empty=True)

        parts = {
            DatePart.year: int(lst[3]),
            DatePart.month: int(getattr(Month, lst[2]).value),
            DatePart.day: int(lst[1]),
            DatePart.day_nm: lst[0],
            DatePart.hour: int(lst[4]),
            DatePart.minute: int(lst[5]),
            DatePart.second: int(lst[6]),
            DatePart.zone_text: lst[7],
            DatePart.zone_sign: False if lst[7][0] == '-' else True if lst[7][0] == '+' else None
        }

        if out_res is None:
            out_res = []

        date = dates.create_date(parts)
        out_res.append(date)

        return True
    except (ValueError, AttributeError, IndexError):
        return False


def is_date_rfc_1123(val, out_res=None):
    """
    Code:       RFC 1123
    Format:     wkday, 2DIGIT month 4DIGIT 2DIGIT:2DIGIT:2DIGIT GMT
    Example:    Sun, 06 Nov 1994 08:49:37 GMT
    """
    try:
        lst = util.split(val, [' ', ',', ':'], remove_empty=True)

        parts = {
            DatePart.year: int(lst[3]),
            DatePart.month: int(getattr(Month, lst[2]).value),
            DatePart.day: int(lst[1]),
            DatePart.day_nm: lst[0],
            DatePart.hour: int(lst[4]),
            DatePart.minute: int(lst[5]),
            DatePart.second: int(lst[6]),
            DatePart.zone_text: '+00:00',
            DatePart.zone_sign: True
        }

        if out_res is None:
            out_res = []

        date = dates.create_date(parts)
        out_res.append(date)

        return True
    except (ValueError, AttributeError, IndexError):
        return False


def is_date_rfc_850(val, out_res=None):
    """
    Code:       RFC 850
    Format:     weekday, 2DIGIT-month-2DIGIT 2DIGIT:2DIGIT:2DIGIT GMT
    Example:    Sunday, 06-Nov-94 08:49:37 GMT
    """
    try:
        lst = util.split(val, ['-', ',', ':', ' '], remove_empty=True)

        parts = {
            DatePart.year: int(lst[3]),
            DatePart.month: int(getattr(Month, lst[2]).value),
            DatePart.day: int(lst[1]),
            DatePart.day_name: lst[0],
            DatePart.hour: int(lst[4]),
            DatePart.minute: int(lst[5]),
            DatePart.second: int(lst[6]),
            DatePart.zone_text: '+00:00',
            DatePart.zone_sign: True
        }

        if out_res is None:
            out_res = []

        date = dates.create_date(parts)
        out_res.append(date)

        return True
    except (ValueError, AttributeError, IndexError):
        return False


def is_date_ansi_c(val, out_res=None):
    """
    Code:       ANSI C's asctime()
    Format:     wkday month 1|2DIGIT 2DIGIT:2DIGIT:2DIGIT 4DIGIT
    Example:    Sun Nov  6 08:49:37 1994
    """
    try:
        lst = util.split(val, [' ', ',', ':'], remove_empty=True)

        parts = {
            DatePart.year: int(lst[6]),
            DatePart.month: int(getattr(Month, lst[1]).value),
            DatePart.day: int(lst[2]),
            DatePart.day_nm: lst[0],
            DatePart.hour: int(lst[3]),
            DatePart.minute: int(lst[4]),
            DatePart.second: int(lst[5])
        }

        if out_res is None:
            out_res = []

        date = dates.create_date(parts)
        out_res.append(date)

        return True
    except (ValueError, AttributeError, IndexError):
        return False


def is_date_rfc_2616(val, out_res=None):
    """
    Code: RFC 2616 (HTTP-date) = rfc1123-date | rfc850-date | asctime-date
    """
    is_valid = is_date_rfc_1123(val, out_res) or is_date_rfc_850(val, out_res) or is_date_ansi_c(val, out_res)
    return is_valid


def is_date(val, out_res=None):
    if out_res is None:
        out_res = []

    if isinstance(val, datetime):
        out_res.append(val)
        return True

    val = dates.replace_zones(val)

    if is_date_rfc_3339(val, out_res):
        return True
    elif is_date_iso_8601(val, out_res):
        return True
    elif is_date_rfc_2822(val, out_res):
        return True
    elif is_date_rfc_2616(val, out_res):
        return True
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
        return val