'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''
from __future__ import absolute_import
from __future__ import division


import calendar
import datetime
import logging
import os
import shutil
import json
import re


MONTHS = {
    1: 'januari',
    2: 'februari',
    3: 'maart',
    4: 'april',
    5: 'mei', 
    6: 'juni',
    7: 'juli',
    8: 'augustus',
    9: 'september',
    10: 'oktober',
    11: 'november',
    12: 'december',
}

ABBREVIATED_MONTHS = {
    'jan':  1,
    'feb':  2,
    'mar':  3,
    'apr':  4,
    'may':  5, 'mei':  5,
    'jun':  6,
    'jul':  7,
    'aug':  8,
    'sep':  9,
    'oct': 10, 'okt': 10,
    'nov': 11,
    'dec': 12,
}


_YEAR_RE      = "(?P<year>[0-9]{4})"
_MONTHNAME_RE = "(?P<monthname>[A-Z][a-z][a-z])"
_MONTH_RE     = "(?P<month>[0-9]{1,2})"
_DAY_RE       = "(?P<day>[0-9]{1,2})"
_DAYNAME_RE   = "(?P<dayname>[A-Z][a-z]*)"
_TIME_RE      = "(?P<hour>[0-9]{1,2}):(?P<minute>[0-9]{2}):(?P<second>[0-9]{2})"
_AM_PM_RE     = "(?P<am_pm>[AP]M)"
_TIMEZONE_RE  = "(?P<tzname>[A-Z]{3,4})"

# US format: 'Apr 5, 2013 10:04:10 AM'
_US_DATE_TIME_RE = _MONTHNAME_RE + "\s+" + _DAY_RE + ",\s+" + _YEAR_RE + "\s+" + _TIME_RE + "\s+" + _AM_PM_RE
# UK format: 'Tue Apr 5 22:10:10 CEST 2013'
_UK_DATE_TIME_RE = _DAYNAME_RE + "\s+" + _MONTHNAME_RE + "\s+" + _DAY_RE + "\s+" + _TIME_RE + "\s+" + _TIMEZONE_RE + "\s+" + _YEAR_RE
# ISO date: '2013-11-05'
_ISO_DATE_RE = _YEAR_RE + "-" + _MONTH_RE + "-" + _DAY_RE


def _parse_date_time( date_time_re, date_time_string):
    ''' Parse a date/time string using a regular expression.
        The regular expression must contain named match groups:
        year - the year in four digits
        monthname - the abbreviate name of the month
        day - the number of the day in the month
        hour, minute, second - the time
        and optional:
        am_pm - used insensitive to case
        '''
    if not isinstance(date_time_string,basestring):
        raise TypeError("date_time_string should be a string, " \
                        "not {cls!r}".format(cls=date_time_string.__class__.__name__))

    m = re.search( date_time_re, date_time_string )
    if m is None:
        raise ValueError("date_time_string {s!r} not matched".format(s=date_time_string))

    year   = int(m.group('year'))
    month  = ABBREVIATED_MONTHS[m.group('monthname').lower()]
    day    = int(m.group('day'))
    hour   = int(m.group('hour'))
    minute = int(m.group('minute'))
    second = int(m.group('second'))
    if m.groupdict().get('am_pm','').lower() == 'pm' and hour < 12:
        hour += 12

    return datetime.datetime(year, month, day, hour, minute, second)


def parse_us_date_time(date_time_string):
    ''' Parse a US format date/time string of the form 
        'Apr 5, 2013 10:04:10 AM'. '''
    return _parse_date_time( _US_DATE_TIME_RE, date_time_string )


def parse_uk_date_time(date_time_string):
    ''' Parse a UK format date/time string of the form 
        'Tue Apr 5 22:10:10 CEST 2013'. '''
    return _parse_date_time( _UK_DATE_TIME_RE, date_time_string )


def parse_iso_date(date_string):
    ''' Parse an ISO format date string of the form '2013-11-05'. '''
    if not isinstance(date_string,basestring):
        raise TypeError("date_string should be a string, " \
                        "not {cls!r}".format(cls=date_string.__class__.__name__))

    m = re.search( _ISO_DATE_RE, date_string )
    if m is None:
        raise ValueError("date_string {s!r} not matched".format(s=date_string))

    year   = int(m.group('year'))
    month  = int(m.group('month'))
    day    = int(m.group('day'))

    return datetime.datetime(year, month, day)


def parse_time_string(time_string):
    ''' Parse a time string of the form '22:10:34'. '''
    if not isinstance(time_string,basestring):
        raise TypeError("time_string should be a string, " \
                        "not {cls!r}".format(cls=time_string.__class__.__name__))

    m = re.search( _TIME_RE, time_string )
    if m is None:
        raise ValueError("time_string {t!r} not matched".format(t=time_string))

    hour   = int(m.group('hour'))
    minute = int(m.group('minute'))
    second = int(m.group('second'))

    return hour, minute, second


def parse_us_int(string):
    ''' Remove , from US format integers. '''
    return int(string.replace(',', ''))


def percentage(numerator, denominator, zero_divided_by_zero_is_zero=False):
    ''' Return numerator / denominator * 100. '''
    if float(denominator) == 0.0:
        if float(numerator) == 0.0 and zero_divided_by_zero_is_zero:
            return 0
        else: 
            return 100
    else:
        return int(round((numerator / denominator) * 100))


def format_date(date_time, year=None):
    ''' Return a (Dutch) formatted version of the datetime. '''
    if date_time:
        formatted_date = '{day} {month}'.format(day=date_time.day, month=MONTHS[date_time.month])
        if year:
            formatted_date += ' {year}'.format(year=date_time.year)
    else:
        formatted_date = 'onbekende datum'
    return formatted_date


def format_month(date):
    ''' Return a (Dutch) formatted version of the month and year. '''
    return '{month} {year}'.format(month=MONTHS[date.month], year=date.year)


def format_timedelta(timedelta):
    ''' Return a (Dutch) formatted version of the timedelta. '''

    days    =  timedelta.days
    hours   =  timedelta.seconds // 3600
    minutes = (timedelta.seconds % 3600) // 60

    if days > 1:
        return '{days} dagen'.format(days=days)

    if days > 0:
        if hours > 0:
            return 'een dag en {hours} uur'.format(hours=hours)
        else:
            return '24 uur'

    if hours > 0:
        result = '{hours} uur'.format(hours=hours)
        if hours < 3 and minutes > 1:
            result += ' en {minutes} minuten'.format(minutes=minutes)
        return result

    if minutes > 1:
        return '{minutes} minuten'.format(minutes=minutes)

    return 'een minuut'


def month_ago(date=None, day_correction=0):
    ''' Return the date that is one month earlier on the same day of the 
        month (or earlier if needed to prevent invalid days). '''
    date  = date or datetime.date.today()
    month = date.month - 1
    year  = date.year
    day   = date.day - day_correction
    while month < 1:
        month += 12
        year  -=  1

    try:
        return date.replace(year=year, month=month, day=day)
    except ValueError:
        return month_ago(date, day_correction + 1)


def last_day_of_month(date):
    ''' Return the day number of the last of the month. '''
    if date.month == 2:
        return 29 if calendar.isleap(date.year) else 28
    else:
        return 31 if date.month in (1, 3, 5, 7, 8, 10, 12) else 30


def workdays_in_period(start_date, end_date):
    ''' Return the number of work days in the period. All days between
        start date and end date are considered, including the start date and
        end date themselves. '''
    return sum( 1
                for ordinal in range(start_date.toordinal(), end_date.toordinal() + 1)
                if datetime.date.fromordinal(ordinal).isoweekday() <= 5
              )


class memoized(object):  # pylint: disable=C0103,R0903
    ''' Decorator. Caches a function's return value each time it is called.
        If called later with the same arguments, the cached value is returned
        (not reevaluated). '''

    def __init__(self, func):
        self.__func = func
        self.__instance = None
        self.__cache = {}

    def __get__(self, instance, cls=None):
        self.__instance = instance
        return self

    def __call__(self, *args, **kwargs):
        key = (id(self.__instance),) + args + \
              tuple([kwargs[key] for key in sorted(kwargs)])
        try:
            return self.__cache[key]
        except KeyError:
            value = self.__func(self.__instance, *args, **kwargs)
            self.__cache[key] = value
            return value
        except TypeError:
            # Not cacheable -- for instance, passing a list as an argument.
            # Better to not cache than to blow up entirely.
            return self.__func(self.__instance, *args, **kwargs)

    def __repr__(self):
        ''' Return the function's docstring. '''
        return self.__func.__doc__


def rmtree(folder, remove_tree=shutil.rmtree, exists=os.path.exists):
    ''' Remove folder recursively. '''
    if exists(folder):
        try:
            remove_tree(folder)
        except OSError, reason:
            logging.warning("Couldn't remove {}: {}".format(folder, reason))


def html_escape(text):
    '''Return the text with all HTML characters escaped. '''
    text = text.replace('&', '&amp;')
    text = text.replace('"', '&quot;')
    text = text.replace("'", '&#39;')
    text = text.replace(">", '&gt;')
    text = text.replace("<", '&lt;')
    return text


def eval_json(json_string):
    ''' Return an evaluated version of the json string. '''
    return json.loads(json_string)
