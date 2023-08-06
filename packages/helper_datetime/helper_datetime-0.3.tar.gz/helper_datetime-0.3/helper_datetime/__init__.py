#!/usr/bin/env python
#-*- coding:utf -*-
import re
import datetime


class HelperDateTime(object):
    """
    rfc5322 Internet Message Format
    RFC 822, 1036, 1123, 2822
    3.3.  Date and Time Specification
    http://tools.ietf.org/html/rfc5322#section-3.3

    Examples:

        Wed, 25 Mar 2015 02:23:56 +0000
        Wednesday, 25-Mar-15 02:23:56 UTC


    rfc3339 Date and Time on the Internet: Timestamps
    http://tools.ietf.org/html/rfc3339

    Examples:

        1990-12-31T23:59:60Z
        1937-01-01T12:00:27.87+00:20


    http://en.wikipedia.org/wiki/ISO_8601
    http://www.iso.org/iso/home/standards/iso8601.htm

    Examples:

        2015-03-24T06:57:23+00:00
        2015-03-24T06:57:23Z

    >>> HelperDateTime(u'光明頂- 20150324 - 新加坡模式').date
    datetime.date(2015, 3, 24)
    """

    PATTERNS = [
        ur'(?P<year>\d{4})(?P<month>\d{2})(?P<day>\d{2})',
        ur'(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})',
        ur'^(?P<year>\d{4})',
    ]

    def __init__(self, s, pattern=None):
        self._datetime = None
        self._parse_datetime(s=s, pattern=pattern)

    def _parse_datetime(self, s, pattern=None):
        if pattern:
            patterns = [pattern]
        else:
            patterns = HelperDateTime.PATTERNS

        for pattern in patterns:
            m = re.search(pattern=pattern, string=s)
            if not m:
                continue

            group_dict = m.groupdict()

            year, month, day = 1, 1, 1
            hour, minute, second = 0, 0, 0

            if 'year' in group_dict:
                year = int(group_dict['year'])

            if 'month' in group_dict:
                month = int(group_dict['month'])

            if 'day' in group_dict:
                day = int(group_dict['day'])

            if 'hour' in group_dict:
                hour = int(group_dict['hour'])

            if 'minute' in group_dict:
                minute = int(group_dict['minute'])

            if 'second' in group_dict:
                second = int(group_dict['second'])

            self._datetime = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
            break

    @property
    def format_in_iso8601(self):
        return self._datetime.isoformat()

    @property
    def format_in_rfc5322(self):
        pass

    @property
    def format_in_rfc3339(self):
        pass

    @property
    def date(self):
        return datetime.date(year=self._datetime.year, month=self._datetime.month, day=self._datetime.day)
