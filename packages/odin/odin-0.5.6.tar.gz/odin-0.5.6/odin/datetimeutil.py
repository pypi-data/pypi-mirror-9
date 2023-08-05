# -*- coding: utf-8 -*-
import datetime
import re
import time
import six
from email.utils import parsedate_tz as parse_http_datetime


ZERO = datetime.timedelta(0)
LOCAL_STD_OFFSET = datetime.timedelta(seconds=-time.timezone)
LOCAL_DST_OFFSET = datetime.timedelta(seconds=-time.altzone) if time.daylight else LOCAL_STD_OFFSET
LOCAL_DST_DIFF = LOCAL_DST_OFFSET - LOCAL_STD_OFFSET


class UTC(datetime.tzinfo):
    """
    UTC timezone.
    """
    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

    def __str__(self):
        return "UTC"

    def __repr__(self):
        return "<timezone: %s>" % self

utc = UTC()


class LocalTimezone(datetime.tzinfo):
    """
    The current local timezone (according to the platform)
    """
    def utcoffset(self, dt):
        return LOCAL_DST_OFFSET if self._is_dst(dt) else LOCAL_STD_OFFSET

    def dst(self, dt):
        return LOCAL_DST_DIFF if self._is_dst(dt) else ZERO

    def tzname(self, dt):
        return time.tzname[self._is_dst(dt)]

    def _is_dst(self, dt):
        stamp = time.mktime((dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday(), 0, 0))
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0

    def __str__(self):
        return time.tzname[0]

    def __repr__(self):
        return "<timezone: %s>" % self

local = LocalTimezone()


class FixedTimezone(datetime.tzinfo):
    """
    A fixed timezone for when a timezone is specified by a numerical offset and no dst information is available.
    """
    __slots__ = ('offset', 'name',)

    @classmethod
    def from_seconds(cls, seconds):
        sign = '-' if seconds < 0 else ''
        minutes = abs(seconds // 60)
        hours = minutes // 60
        minutes %= 60
        name = "%s%02d:%02d" % (sign, hours, minutes)

        if sign == '-':
            hours *= -1
            minutes *= -1

        return cls(datetime.timedelta(hours=hours, minutes=minutes), name)

    @classmethod
    def from_hours_minutes(cls, hours, minutes):
        sign = '-' if hours < 0 else ''
        hours = abs(hours)
        minutes = abs(minutes)
        name = "%s%02d:%02d" % (sign, hours, minutes)

        if sign == '-':
            hours *= -1
            minutes *= -1

        return cls(datetime.timedelta(hours=hours, minutes=minutes), name)

    @classmethod
    def from_groups(cls, groups, default_timezone=utc):
        tz = groups['timezone']
        if tz is None:
            return default_timezone

        if tz in ('Z', 'GMT', 'UTC'):
            return utc

        sign = groups['tz_sign']
        hours = int(groups['tz_hour'])
        minutes = int(groups['tz_minute'] or 0)
        name = "%s%02d:%02d" % (sign, hours, minutes)

        if sign == '-':
            hours = -hours
            minutes = -minutes

        return cls(datetime.timedelta(hours=hours, minutes=minutes), name)

    def __init__(self, offset=None, name=None):
        super(FixedTimezone, self).__init__()
        self.offset = offset or datetime.timedelta(0)
        self.name = name or ''

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return ZERO

    def tzname(self, dt):
        return self.name

    def __str__(self):
        return self.name

    def __repr__(self):
        return "<timezone %r %r>" % (self.name, self.offset)

    def __eq__(self, other):
        return self.offset == other.offset

    # Pickle support

    def __getstate__(self):
        return {
            'offset': self.offset,
            'name': self.name,
        }

    def __setstate__(self, state):
        self.offset = state.get('offset')
        self.name = state.get('name')


def get_tz_aware_dt(dt, assumed_tz=local):
    """
    Get a time zone aware date time from a supplied date time.

    If dt is already timezone aware it will be returned unchanged.
    If dt is not aware it will be assumed that dt is in local time.
    """
    assert isinstance(dt, datetime.datetime)

    if dt.tzinfo:
        return dt
    else:
        return dt.replace(tzinfo=assumed_tz)


def now_utc():
    """
    Get now in UTC (with timezone set correctly).
    """
    return datetime.datetime.now(tz=utc)


def now_local():
    """
    Get now in the current local timezone.
    """
    return datetime.datetime.now(tz=local)


ISO8601_DATE_STRING_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})$")
ISO8601_TIME_STRING_RE = re.compile(
    r"^(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(\.(?P<microseconds>\d+))?"
    r"(?P<timezone>Z|((?P<tz_sign>[-+])(?P<tz_hour>\d{2})(:(?P<tz_minute>\d{2}))?))?$")
ISO8601_DATETIME_STRING_RE = re.compile(
    r"^(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})[tT\s]"
    r"(?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})(\.(?P<microseconds>\d+))? ?"
    r"(?P<timezone>Z|GMT|UTC|((?P<tz_sign>[-+])(?P<tz_hour>\d{2})(:?(?P<tz_minute>\d{2}))?))?$")


def parse_iso_date_string(date_string):
    """
    Parse a date in the string format defined in ISO 8601.
    """
    if not isinstance(date_string, six.string_types):
        raise ValueError("Expected string")

    matches = ISO8601_DATE_STRING_RE.match(date_string)
    if not matches:
        raise ValueError("Expected ISO 8601 formatted date string.")

    groups = matches.groupdict()
    return datetime.date(
        int(groups['year']),
        int(groups['month']),
        int(groups['day']),
    )


def parse_iso_time_string(time_string, default_timezone=utc):
    """
    Parse a time in the string format defined in ISO 8601.
    """
    if not isinstance(time_string, six.string_types):
        raise ValueError("Expected string")

    matches = ISO8601_TIME_STRING_RE.match(time_string)
    if not matches:
        raise ValueError("Expected ISO 8601 formatted time string.")

    groups = matches.groupdict()
    tz = FixedTimezone.from_groups(groups, default_timezone)
    return datetime.time(
        int(groups['hour']),
        int(groups['minute']),
        int(groups['second']),
        int(groups['microseconds'] or 0),
        tz
    )


def parse_iso_datetime_string(datetime_string, default_timezone=utc):
    """
    Parse a datetime in the string format defined in ISO 8601.
    """
    if not isinstance(datetime_string, six.string_types):
        raise ValueError("Expected string")

    matches = ISO8601_DATETIME_STRING_RE.match(datetime_string)
    if not matches:
        raise ValueError("Expected ISO 8601 formatted datetime string.")

    groups = matches.groupdict()
    tz = FixedTimezone.from_groups(groups, default_timezone)
    return datetime.datetime(
        int(groups['year']),
        int(groups['month']),
        int(groups['day']),
        int(groups['hour']),
        int(groups['minute']),
        int(groups['second']),
        int(groups['microseconds'] or 0),
        tz
    )


def to_ecma_datetime_string(dt, default_timezone=local):
    """
    Convert a python datetime into the string format defined in ECMA-262.

    See ECMA international standard: ECMA-262 section 15.9.1.15

    ``assume_local_time`` if true will assume the date time is in local time if the object is a naive date time object;
        else assumes the time value is utc.
    """
    assert isinstance(dt, datetime.datetime)

    dt = get_tz_aware_dt(dt, default_timezone).astimezone(utc)
    return "%4i-%02i-%02iT%02i:%02i:%02i.%03iZ" % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.microsecond/1000)


def parse_http_datetime_string(datetime_string):
    """
    Parse a datetime in the string format defined in ISO-1123 (or HTTP date time).
    """
    elements = None
    if isinstance(datetime_string, six.string_types):
        elements = parse_http_datetime(datetime_string)

    if not elements:
        raise ValueError("Expected ISO-1123 formatted datetime string.")

    return datetime.datetime(*elements[:6], tzinfo=FixedTimezone.from_seconds(elements[-1]))
