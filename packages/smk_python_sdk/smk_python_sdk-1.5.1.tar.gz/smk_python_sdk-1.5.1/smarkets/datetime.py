# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
from email.utils import mktime_tz, parsedate_tz

import iso8601
import pytz

__all__ = (
    'rfc2822_to_datetime',

    'iso8601_to_datetime',
    'datetime_to_iso8601',
    'parse_datetime',

    'iso8601_to_date',
    'date_to_iso8601',

    'iso8601_to_time',
    'time_to_iso8601',
)


def rfc2822_to_datetime(rfc_date):
    """Converts a RFC 2822 date string to a Python datetime"""
    timestamp = mktime_tz(parsedate_tz(rfc_date))
    raw_dt = datetime.datetime.utcfromtimestamp(timestamp)
    return raw_dt.replace(tzinfo=pytz.utc)


def iso8601_to_datetime(iso_date, naive=False):
    """Converts an ISO-8601 date string to a Python datetime.

    Usage: >>> iso8601_to_datetime('2009-04-24T15:48:26,483772Z')
           datetime.datetime(2009, 04, 24, 15, 48, 26, 483772)
    """
    if iso_date is None:
        return None
    iso_date = iso_date.replace(',', '.')
    try:
        new_date = iso8601.parse_date(iso_date).astimezone(pytz.utc)
        if naive:
            new_date = new_date.replace(tzinfo=None)
    except iso8601.ParseError:
        new_date = None
    return new_date


def parse_datetime(iso):
    """Convert ISO8601 formatted timestamp to timezone-naive, UTC-normalized datetime object."""
    return iso8601.parse_date(iso).astimezone(pytz.utc).replace(tzinfo=None)


def iso8601_to_date(iso_date):
    """As above, but just returns a date object"""
    return iso8601_to_datetime(iso_date + 'T00:00:00').date()


def date_to_iso8601(date):
    """Converts a date to an ISO 8601 date"""
    return '%s-%02d-%02d' % (date.year, date.month, date.day)


def datetime_to_iso8601(date_time):
    """Converts a date/time to an ISO8601 date string"""
    assert not date_time.utcoffset()
    return date_time.strftime('%Y-%m-%dT%H:%M:%S.%f') + 'Z'


def time_to_iso8601(time):
    return time.strftime('%H:%M:%S')


def iso8601_to_time(time):
    try:
        hour, minute, second = time.split(':')
        return datetime.time(int(hour), int(minute), int(second))
    except (ValueError, AttributeError):
        return None
