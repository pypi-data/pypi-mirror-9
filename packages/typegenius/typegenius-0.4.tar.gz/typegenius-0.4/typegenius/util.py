import re


def split(value, delimiters, remove_empty=False):
    parts = re.split('|'.join(delimiters), value)
    if remove_empty:
        parts = list(p for p in parts if len(p) > 0)
    return parts