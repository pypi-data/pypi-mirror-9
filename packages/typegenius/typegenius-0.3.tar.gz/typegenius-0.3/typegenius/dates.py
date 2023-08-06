from enum import Enum
from datetime import datetime
from typegenius import localization, util


class Month(Enum):
    Jan = 1
    Feb = 2
    Mar = 3
    Apr = 4
    May = 5
    Jun = 6
    Jul = 7
    Aug = 8
    Sep = 9
    Oct = 10
    Nov = 11
    Dec = 12


class Wkday(Enum):
    Mon = 1
    Tue = 2
    Wed = 3
    Thu = 4
    Fri = 5
    Sat = 6
    Sun = 7


class Weekday(Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    Sunday = 7


class DatePart(Enum):
    year = 1
    month = 2
    day = 3
    day_nm = 4
    day_name = 5

    t = 6
    hour = 7
    minute = 8
    second = 9
    fraction = 10

    zone_text = 11
    zone_sign = 12
    zone_h = 13
    zone_m = 14


def pad_year(year):
    if 59 <= year <= 99:
        return '19{0}'.format(str(year).zfill(2))
    else:
        return '20{0}'.format(str(year).zfill(2))


def replace_zones(val):
    res = val\
        .replace('Z', '+00:00')\
        .replace('GMT', '+00:00')\
        .replace('UTC', '+00:00')\
        .replace('EST', '-05:00')\
        .replace('EDT', '-04:00')\
        .replace('CST', '-06:00')\
        .replace('CDT', '-05:00')\
        .replace('MST', '-07:00')\
        .replace('MDT', '-06:00')\
        .replace('PST', '-08:00')\
        .replace('PDT', '-07:00')
    return res


def create_date(parts):
    lst = [pad_year(parts[DatePart.year]) if parts[DatePart.year] <= 99 else str(parts[DatePart.year])]
    frm = '%Y'
    if parts[DatePart.month] is not None:
        lst.append(str(parts[DatePart.month]).zfill(2))
        frm += ' %m'
        if DatePart.day_nm in parts and parts[DatePart.day_nm] is not None:
            lst.append(parts[DatePart.day_nm])
            frm += ' %a'
        elif DatePart.day_name in parts and parts[DatePart.day_name] is not None:
            lst.append(parts[DatePart.day_name])
            frm += ' %A'
        if DatePart.day in parts and parts[DatePart.day] is not None:
            lst.append(str(parts[DatePart.day]).zfill(2))
            frm += ' %d'
            if DatePart.hour in parts and parts[DatePart.hour] is not None:
                lst.append(str(parts[DatePart.hour]).zfill(2))
                frm += ' %H'
                if DatePart.minute in parts and parts[DatePart.minute] is not None:
                    lst.append(str(parts[DatePart.minute]).zfill(2))
                    frm += ' %M'
                    if DatePart.second in parts and parts[DatePart.second] is not None:
                        if parts[DatePart.second] % 1 > 0:
                            lst.append(str(parts[DatePart.second]).zfill(2))
                            frm += ' %S.%f'
                        else:
                            lst.append(str(int(parts[DatePart.second])).zfill(2))
                            frm += ' %S'
                        if DatePart.zone_sign in parts and parts[DatePart.zone_sign] is not None:
                            lst.append(parts[DatePart.zone_text].replace(':', ''))
                            frm += ' %z'
    res = datetime.strptime(' '.join(lst), frm)
    return res


def get_descending_parts(val):
    res = {
        DatePart.year: None,
        DatePart.month: None,
        DatePart.day: None,
        DatePart.t: None,
        DatePart.hour: None,
        DatePart.minute: None,
        DatePart.second: None,
        DatePart.fraction: None,
        DatePart.zone_text: None,
        DatePart.zone_sign: None,
        DatePart.zone_h: None,
        DatePart.zone_m: None
    }

    dc = localization.get_decimal_separator()
    date_time_zone_parts = util.split(val, [' ', 'T'])
    date_parts = util.split(date_time_zone_parts[0], ['-'])
    time_zone_parts = time_parts = zone_parts = []

    if len(date_time_zone_parts) > 1:
        time_zone_parts = util.split(date_time_zone_parts[1], ['\+', '-', 'Z'])
        time_parts = util.split(time_zone_parts[0].replace(',', dc).replace('.', dc), [':'])
        index_list = list(i for i, v in enumerate(date_time_zone_parts[1]) if v in '\+|-|Z')
        zone_parts = util.split(date_time_zone_parts[1][index_list[0]:], [':']) if len(index_list) > 0 else []

    # Date
    if len(date_parts) > 0 and date_parts[0].isdigit() and len(date_parts[0]) == 4:
        res[DatePart.year] = int(date_parts[0])
    if len(date_parts) > 1 and date_parts[1].isdigit():
        res[DatePart.month] = int(date_parts[1])
    if len(date_parts) > 2 and date_parts[2].isdigit():
        res[DatePart.day] = int(date_parts[2])

    # Time
    if len(date_time_zone_parts) > 1:
        res[DatePart.t] = val.strip().replace(date_time_zone_parts[0], '').replace(date_time_zone_parts[1], '')
    if len(time_parts) > 0 and time_parts[0].isdigit():
        res[DatePart.hour] = int(time_parts[0])
    if len(time_parts) > 1 and time_parts[1].isdigit():
        res[DatePart.minute] = int(time_parts[1])
    if len(time_parts) > 2:
        res[DatePart.second] = float(time_parts[2])
    if len(time_zone_parts) > 0:
        res[DatePart.fraction] = ',' if ',' in time_zone_parts[0] else '.' if '.' in time_zone_parts[0] else None

    # Zone
    if len(zone_parts) > 0:
        res[DatePart.zone_text] = ':'.join(zone_parts)
        res[DatePart.zone_sign] = False if zone_parts[0][0] == '-' else True if zone_parts[0][0] == '+' else None
        res[DatePart.zone_h] = int(zone_parts[0]) if zone_parts[0].isdigit() else 0
    if len(zone_parts) > 1:
        res[DatePart.zone_m] = int(zone_parts[1]) if len(zone_parts) > 1 and zone_parts[1].isdigit() else 0

    return res