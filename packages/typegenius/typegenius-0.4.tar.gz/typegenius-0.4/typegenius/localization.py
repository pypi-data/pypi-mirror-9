import locale


def get_decimal_separator():
    env = locale.localeconv()
    return env['decimal_point']


def get_thou_separator():
    env = locale.localeconv()
    return env['thousands_sep']