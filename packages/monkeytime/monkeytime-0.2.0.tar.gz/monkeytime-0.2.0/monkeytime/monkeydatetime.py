#!/usr/bin/env python
''' monkeydatetime
Builds the custom strptime and patches datetime.
'''

import re
import datetime as _datetime

RE_DIRECTIVES = re.compile(r'%\w')
SUPPORTED_DIRECTIVES = ('%d', '%m', '%Y', '%H', '%M', '%S', '%f')
DIRECTIVES_LENGTH = {
    '%d': 2,
    '%m': 2,
    '%y': 2,
    '%Y': 4,
    '%H': 2,
    '%M': 2,
    '%S': 2,
    '%f': 6,
}

DIRECTIVES_NAME = {
    '%d': 'day',
    '%m': 'month',
    '%y': 'year',
    '%Y': 'year',
    '%H': 'hour',
    '%M': 'minute',
    '%S': 'second',
    '%f': 'microsecond',
}
KWARGS_NAMES = set(DIRECTIVES_NAME.values())
KWARGS_NAMES.remove('year')
DEFAULT_VALUES = {
    'year': 1900, 'month': 1, 'day': 1,
    'hour': 0, 'minute': 0, 'second': 0, 
    'microsecond': 0,
}

def lengthen_dt_format(dt_format_orig):
    dt_format = dt_format_orig.replace('%Y', '%Y  ')
    dt_format = dt_format.replace('%f', '%f    ')
    return dt_format

def build_strptime(dt_format_orig):
    dt_format = lengthen_dt_format(dt_format_orig)

    default_slices = {}
    for direc, dlen in DIRECTIVES_LENGTH.items():
        if direc in dt_format:
            name = DIRECTIVES_NAME[direc]
            start = dt_format.find(direc)
            end = start + DIRECTIVES_LENGTH[direc]
            default_slices[name] = '[%s:%s]' % (start, end)
    
    new_strptime_code = """
def new_strptime(dt_string):
    return _datetime.datetime(%s)
"""
    kwargs = ''
    for name, val in DEFAULT_VALUES.items():
        if name in default_slices:
            kwargs += '%s=int(dt_string%s),' % (name, default_slices[name])
        else:
            kwargs += '%s=%s,' % (name, val)
    code = new_strptime_code % kwargs
    exec(code)
    return new_strptime

class datetime(_datetime.datetime):
    _old_strptime = _datetime.datetime.strptime
    _memoized_strptime = {}
    # Sticking to the simplest padded directives to speed up

    @classmethod
    def supported_strptime(cls, dt_format):
        directives = RE_DIRECTIVES.findall(dt_format)
        if not directives:
            return False
        for directive in directives:
            if directive not in SUPPORTED_DIRECTIVES:
                return False
        return True

    @classmethod
    def __build_strptime(cls, dt_format):
        if not cls.supported_strptime(dt_format):
            cls._memoized_strptime[dt_format] = None
            return None
        func = build_strptime(dt_format)
        cls._memoized_strptime[dt_format] = func
        return func

    @classmethod
    def __get_strptime(cls, dt_format):
        ''' Builds your custom strptime function '''
        if dt_format in cls._memoized_strptime:
            return cls._memoized_strptime[dt_format]
        return cls.__build_strptime(dt_format)
    
    @classmethod
    def strptime(cls, dt_string, dt_format):
        ''' strptime to patch in '''
        func = cls.__get_strptime(dt_format)
        if func is None:
            # Not supported, revert to old version
            return cls._old_strptime(dt_string, dt_format)
        return func(dt_string)
