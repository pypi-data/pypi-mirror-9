import pytz
import parsedatetime
from flask.ext.babel import gettext, ngettext
from delorean import Delorean, DeloreanInvalidTimezone, parse as dparse
from datetime import timedelta, datetime, date
from babel.dates import format_datetime
from babel.core import default_locale


LC_TIME = default_locale('LC_TIME')


def parse(s, dayfirst=True, yearfirst=True):
    do = dparse(s, dayfirst, yearfirst)
    return Datetime2(datetime=do._dt, timezone=do._tz)


_US_TIMEZONES = [
    ("-1000", "US/Hawaii", '(GMT-1000)', 'Hawaii'),
    ("-0900", "US/Alaska", '(GMT-0900)', 'Alaska'),
    ("-0800", "US/Pacific", '(GMT-0800)', 'Pacific Time (US & Canada)'),
    ("-0700", "US/Arizona", '(GMT-0700)', 'Arizona'),
    ("-0700", "US/Mountain", '(GMT-0700)', 'Mountain Time (US & Canada)'),
    ("-0600", "US/Central", '(GMT-0600)', 'Central Time (US & Canada)'),
    ("-0500", "US/Eastern", '(GMT-0500)', 'Eastern Time (US & Canada)'),
    ("-0500", "US/East-Indiana", '(GMT-0500)', 'Indiana (East)'),
]


_ALL_TIMEZONES = [
    ("-1100", "Pacific/Midway", '(GMT-1100)', 'International Date Line West'),
    ("-1100", "Pacific/Midway", '(GMT-1100)', 'Midway Island'),
    ("-1100", "Pacific/Samoa", '(GMT-1100)', 'Samoa'),
    ("-1000", "US/Hawaii", '(GMT-1000)', 'Hawaii'),
    ("-0900", "US/Alaska", '(GMT-0900)', 'Alaska'),
    ("-0800", "US/Pacific", '(GMT-0800)', 'Pacific Time (US & Canada)'),
    ("-0800", "America/Tijuana", '(GMT-0800)', 'Tijuana'),
    ("-0700", "US/Arizona", '(GMT-0700)', 'Arizona'),
    ("-0700", "America/Chihuahua", '(GMT-0700)', 'Chihuahua'),
    ("-0700", "America/Mazatlan", '(GMT-0700)', 'Mazatlan'),
    ("-0700", "US/Mountain", '(GMT-0700)', 'Mountain Time (US & Canada)'),
    ("-0600", "Canada/Central", '(GMT-0600)', 'Central America'),
    ("-0600", "Canada/Central", '(GMT-0600)', 'Central Time (US & Canada)'),
    ("-0600", "Mexico/General", '(GMT-0600)', 'Guadalajara'),
    ("-0600", "Mexico/General", '(GMT-0600)', 'Mexico City'),
    ("-0600", "America/Monterrey", '(GMT-0600)', 'Monterrey'),
    ("-0600", "Canada/Saskatchewan", '(GMT-0600)', 'Saskatchewan'),
    ("-0500", "America/Bogota", '(GMT-0500)', 'Bogota'),
    ("-0500", "US/Eastern", '(GMT-0500)', 'Eastern Time (US & Canada)'),
    ("-0500", "US/East-Indiana", '(GMT-0500)', 'Indiana (East)'),
    ("-0500", "America/Lima", '(GMT-0500)', 'Lima'),
    ("-0500", "Etc/GMT-5", '(GMT-0500)', 'Quito'),
    ("-0430", "America/Caracas", '(GMT-0430)', 'Caracas'),
    ("-0400", "Canada/Atlantic", '(GMT-0400)', 'Atlantic Time (Canada)'),
    ("-0400", "Etc/GMT-4", '(GMT-0400)', 'La Paz'),
    ("-0400", "America/Santiago", '(GMT-0400)', 'Santiago'),
    ("-0400", "America/Cuiaba", '(GMT-0400)', 'Mato Grosso'),
    ("-0330", "Canada/Newfoundland", '(GMT-0330)', 'Newfoundland'),
    ("-0300", "Brazil/East", '(GMT-0300)', 'Brasilia'),
    ("-0300", "America/Argentina/Buenos_Aires", '(GMT-0300)', 'Buenos Aires'),
    ("-0300", "America/Guyana", '(GMT-0300)', 'Georgetown'),
    ("-0300", "America/Godthab", '(GMT-0300)', 'Greenland'),
    ("-0300", "America/Fortaleza", '(GMT-0300)', 'NE Brazil'),
    ("-0100", "Atlantic/Azores", '(GMT-0100)', 'Azores'),
    ("-0100", "Atlantic/Cape_Verde", '(GMT-0100)', 'Cape Verde Is. '),
    ("+0000", "Africa/Casablanca", '(GMT+0000)', 'Casablanca'),
    ("+0000", "Europe/Dublin", '(GMT+0000)', 'Dublin'),
    ("+0000", "Europe/London", '(GMT+0000)', 'Edinburgh'),
    ("+0000", "Europe/Lisbon", '(GMT+0000)', 'Lisbon'),
    ("+0000", "Europe/London", '(GMT+0000)', 'London'),
    ("+0000", "Africa/Monrovia", '(GMT+0000)', 'Monrovia'),
    ("+0000", "UTC", '(GMT+0000)', 'UTC'),
    ("+0100", "Europe/Amsterdam", '(GMT+0100)', 'Amsterdam'),
    ("+0100", "Europe/Belgrade", '(GMT+0100)', 'Belgrade'),
    ("+0100", "Europe/Berlin", '(GMT+0100)', 'Berlin'),
    ("+0100", "Europe/Zurich", '(GMT+0100)', 'Bern'),
    ("+0100", "Europe/Bratislava", '(GMT+0100)', 'Bratislava'),
    ("+0100", "Europe/Brussels", '(GMT+0100)', 'Brussels'),
    ("+0100", "Europe/Budapest", '(GMT+0100)', 'Budapest'),
    ("+0100", "Europe/Copenhagen", '(GMT+0100)', 'Copenhagen'),
    ("+0100", "Europe/Ljubljana", '(GMT+0100)', 'Ljubljana'),
    ("+0100", "Europe/Madrid", '(GMT+0100)', 'Madrid'),
    ("+0100", "Europe/Paris", '(GMT+0100)', 'Paris'),
    ("+0100", "Europe/Prague", '(GMT+0100)', 'Prague'),
    ("+0100", "Europe/Rome", '(GMT+0100)', 'Rome'),
    ("+0100", "Europe/Sarajevo", '(GMT+0100)', 'Sarajevo'),
    ("+0100", "Europe/Skopje", '(GMT+0100)', 'Skopje'),
    ("+0100", "Europe/Stockholm", '(GMT+0100)', 'Stockholm'),
    ("+0100", "Europe/Vienna", '(GMT+0100)', 'Vienna'),
    ("+0100", "Europe/Warsaw", '(GMT+0100)', 'Warsaw'),
    ("+0100", "Europe/Copenhagen", '(GMT+0100)', 'West Central Africa'),
    ("+0100", "Europe/Zagreb", '(GMT+0100)', 'Zagreb'),
    ("+0200", "Europe/Athens", '(GMT+0200)', 'Athens'),
    ("+0200", "Europe/Bucharest", '(GMT+0200)', 'Bucharest'),
    ("+0200", "Africa/Cairo", '(GMT+0200)', 'Cairo'),
    ("+0200", "Africa/Harare", '(GMT+0200)', 'Harare'),
    ("+0200", "Europe/Helsinki", '(GMT+0200)', 'Helsinki'),
    ("+0200", "Europe/Istanbul", '(GMT+0200)', 'Istanbul'),
    ("+0200", "Asia/Jerusalem", '(GMT+0200)', 'Jerusalem'),
    ("+0200", "Europe/Kiev", '(GMT+0200)', 'Kyiv'),
    ("+0200", "Europe/Minsk", '(GMT+0200)', 'Minsk'),
    ("+0200", "Africa/Johannesburg", '(GMT+0200)', 'Pretoria'),
    ("+0200", "Europe/Riga", '(GMT+0200)', 'Riga'),
    ("+0200", "Europe/Sofia", '(GMT+0200)', 'Sofia'),
    ("+0200", "Europe/Tallinn", '(GMT+0200)', 'Tallinn'),
    ("+0200", "Europe/Vilnius", '(GMT+0200)', 'Vilnius'),
    ("+0300", "Asia/Baghdad", '(GMT+0300)', 'Baghdad'),
    ("+0300", "Asia/Kuwait", '(GMT+0300)', 'Kuwait'),
    ("+0300", "Europe/Moscow", '(GMT+0300)', 'Moscow'),
    ("+0300", "Africa/Nairobi", '(GMT+0300)', 'Nairobi'),
    ("+0300", "Asia/Riyadh", '(GMT+0300)', 'Riyadh'),
    ("+0300", "Europe/Moscow", '(GMT+0300)', 'St. Petersburg'),
    ("+0300", "Europe/Volgograd", '(GMT+0300)', 'Volgograd'),
    ("+0330", "Asia/Tehran", '(GMT+0330)', 'Tehran'),
    ("+0400", "Asia/Dubai", '(GMT+0400)', 'Abu Dhabi'),
    ("+0400", "Asia/Baku", '(GMT+0400)', 'Baku'),
    ("+0400", "Asia/Muscat", '(GMT+0400)', 'Muscat'),
    ("+0400", "Asia/Tbilisi", '(GMT+0400)', 'Tbilisi'),
    ("+0400", "Asia/Yerevan", '(GMT+0400)', 'Yerevan'),
    ("+0430", "Asia/Kabul", '(GMT+0430)', 'Kabul'),
    ("+0500", "Asia/Karachi", '(GMT+0500)', 'Islamabad'),
    ("+0500", "Asia/Karachi", '(GMT+0500)', 'Karachi'),
    ("+0500", "Asia/Tashkent", '(GMT+0500)', 'Tashkent'),
    ("+0530", "Asia/Calcutta", '(GMT+0530)', 'Chennai'),
    ("+0530", "Asia/Calcutta", '(GMT+0530)', 'Kolkata'),
    ("+0530", "Asia/Calcutta", '(GMT+0530)', 'Mumbai'),
    ("+0530", "Asia/Calcutta", '(GMT+0530)', 'New Delhi'),
    ("+0530", "Asia/Calcutta", '(GMT+0530)', 'Sri Jayawardenepura'),
    ("+0545", "Asia/Kathmandu", '(GMT+0545)', 'Kathmandu'),
    ("+0600", "Asia/Almaty", '(GMT+0600)', 'Almaty'),
    ("+0600", "Asia/Qyzylorda", '(GMT+0600)', 'Astana'),
    ("+0600", "Asia/Dhaka", '(GMT+0600)', 'Dhaka'),
    ("+0600", "Asia/Novosibirsk", '(GMT+0600)', 'Novosibirsk'),
    ("+0630", "Asia/Rangoon", '(GMT+0630)', 'Rangoon'),
    ("+0700", "Asia/Bangkok", '(GMT+0700)', 'Bangkok'),
    ("+0700", "Asia/Saigon", '(GMT+0700)', 'Hanoi'),
    ("+0700", "Asia/Jakarta", '(GMT+0700)', 'Jakarta'),
    ("+0700", "Asia/Krasnoyarsk", '(GMT+0700)', 'Krasnoyarsk'),
    ("+0800", "Asia/Harbin", '(GMT+0800)', 'Beijing'),
    ("+0800", "Asia/Chongqing", '(GMT+0800)', 'Chongqing'),
    ("+0800", "Asia/Hong_Kong", '(GMT+0800)', 'Hong Kong'),
    ("+0800", "Asia/Irkutsk", '(GMT+0800)', 'Irkutsk'),
    ("+0800", "Asia/Kuala_Lumpur", '(GMT+0800)', 'Kuala Lumpur'),
    ("+0800", "Australia/Perth", '(GMT+0800)', 'Perth'),
    ("+0800", "Singapore", '(GMT+0800)', 'Singapore'),
    ("+0800", "Asia/Taipei", '(GMT+0800)', 'Taipei'),
    ("+0800", "Asia/Taipei", '(GMT+0800)', 'Ulaan Bataar'),
    ("+0800", "Asia/Taipei", '(GMT+0800)', 'Urumqi'),
    ("+0900", "Japan", '(GMT+0900)', 'Osaka'),
    ("+0900", "Japan", '(GMT+0900)', 'Sapporo'),
    ("+0900", "Japan", '(GMT+0900)', 'Seoul'),
    ("+0900", "Japan", '(GMT+0900)', 'Tokyo'),
    ("+0900", "Asia/Yakutsk", '(GMT+0900)', 'Yakutsk'),
    ("+0930", "Australia/Adelaide", '(GMT+0930)', 'Adelaide'),
    ("+0930", "Australia/Darwin", '(GMT+0930)', 'Darwin'),
    ("+1000", "Australia/Brisbane", '(GMT+1000)', 'Brisbane'),
    ("+1000", "Australia/Canberra", '(GMT+1000)', 'Canberra'),
    ("+1000", "Pacific/Guam", '(GMT+1000)', 'Guam'),
    ("+1000", "Australia/Hobart", '(GMT+1000)', 'Hobart'),
    ("+1000", "Australia/Melbourne", '(GMT+1000)', 'Melbourne'),
    ("+1000", "Pacific/Port_Moresby", '(GMT+1000)', 'Port Moresby'),
    ("+1000", "Australia/Sydney", '(GMT+1000)', 'Sydney'),
    ("+1000", "Asia/Vladivostok", '(GMT+1000)', 'Vladivostok'),
    ("+1100", "Asia/Magadan", '(GMT+1100)', 'Magadan'),
    ("+1100", "Pacific/Noumea", '(GMT+1100)', 'New Caledonia'),
    ("+1100", "Pacific/Guadalcanal", '(GMT+1100)', 'Solomon Is.'),
    ("+1200", "Pacific/Auckland", '(GMT+1200)', 'Auckland'),
    ("+1200", "Pacific/Fiji", '(GMT+1200)', 'Fiji'),
    ("+1200", "Asia/Kamchatka", '(GMT+1200)', 'Kamchatka'),
    ("+1200", "Asia/Kamchatka", '(GMT+1200)', 'Marshall Is.'),
    ("+1200", "Pacific/Auckland", '(GMT+1200)', 'Wellington'),
    ("+1300", "Pacific/Tongatapu", '(GMT+1300)', 'Nuku\'alofa')
]

timezones = [{"value": tz_tuple[1], "text": "{} ({}:{})".format(tz_tuple[3], tz_tuple[2][4:7], tz_tuple[2][7:-1])} for tz_tuple in list(_US_TIMEZONES + _ALL_TIMEZONES)]


class Datetime2(Delorean):

    def __init__(self, datetime=None, timezone=None):
        timezone = 'UTC' if timezone is None else timezone
        super(Datetime2, self).__init__(datetime=datetime, timezone=timezone)

    def __add__(self, other):
        return Datetime2(datetime=self.datetime + other, timezone=self.timezone)

    def __sub__(self, other):
        if isinstance(other, timedelta):
            return Datetime2(datetime=self.datetime - other, timezone=self.timezone)
        elif isinstance(other, Datetime2):
            return self._dt - other.convert(self._tz)._dt

    def __repr__(self):
        return 'Datetime2(datetime=%s, timezone=%s)' % (self._dt, self._tz)

    def convert(self, tz):
        """
        A shift()-el ellentétben itt nem helyben mozgatjuk a dátumot, hanem új objectet hozunk létre!
        """
        try:
            zone = pytz.timezone(tz)
        except pytz.UnknownTimeZoneError:
            raise DeloreanInvalidTimezone('Provide a valid timezone')
        return Datetime2(datetime=zone.normalize(self._dt), timezone=tz)

    def isoformat(self):
        return self.datetime.isoformat()

    def to_momentjs(self):
        return self.datetime.isoformat()[:-6]

    def midnight(self):
        return Datetime2(datetime=super().midnight())

    @staticmethod
    def now():
        return Datetime2()

    @classmethod
    def fromtimestamp(cls, timestamp, timezone=None):
        return cls(datetime=datetime.fromtimestamp(timestamp), timezone=timezone)

    @classmethod
    def fromutctimestamp(cls, timestamp, timezone=None):
        return cls(datetime=datetime.utcfromtimestamp(timestamp), timezone=timezone)

    @classmethod
    def fromparsedatetime(cls, date_str, timezone='Europe/Budapest'):
        calendar = parsedatetime.Calendar()  # FIXME?
        dt = calendar.parseDT(date_str, tzinfo=pytz.timezone(timezone or 'Europe/Budapest'))[0]
        return cls(dt).convert('UTC')

    @classmethod
    def strptime(cls, date_string, format):
        return cls(datetime=datetime.strptime(date_string, format))

    def strftime(self, format):
        return self._dt.strftime(format)

    def date(self):
        return super().date

    @classmethod
    def parse_date(cls, date_str, timezone=None):
        return cls(parse(date_str).naive(), timezone=timezone)

    @classmethod
    def init_as_datetime(cls, year, month, day, hour=0, minute=0, second=0, microsecond=0, timezone=None):
        return cls(datetime=datetime(year, month, day, hour, minute, second, microsecond), timezone=timezone)

    def timesince(self, dt=None):
        if dt is None:
            dt = Datetime2()
        diff = dt - self
        if diff.days // 365 > 0:
            return ngettext('%(num)s year ago', '%(num)s years ago', num=diff.days // 365)
        elif diff.days // 30 > 0:
            return ngettext('%(num)s month ago', '%(num)s months ago', num=diff.days // 30)
        elif diff.days // 7 > 0:
            return ngettext('%(num)s week ago', '%(num)s weeks ago', num=diff.days // 7)
        elif diff.days > 0:
            return ngettext('%(num)s day ago', '%(num)s days ago', num=diff.days)
        elif diff.seconds // 3600 > 0:
            return ngettext('%(num)s hour ago', '%(num)s hours ago', num=diff.seconds // 3600)
        elif diff.seconds // 60 > 0:
            return ngettext('%(num)s minute ago', '%(num)s minutes ago', num=diff.seconds // 60)
        else:
            return gettext('just now')

DAY_STEP_TS = 86400000

Datetime2.min = Datetime2(datetime=datetime.min)
Datetime2.max = Datetime2(datetime=datetime.max)


class Date2(date):
    pass


class DateFormat(object):
    MDY = 'MDY'
    DMY = 'DMY'
    YMD = 'YMD'

    available_formats = [MDY, DMY, YMD]

    _repr_short = {MDY: "MM/DD/YYYY",
                   DMY: "DD/MM/YYYY",
                   YMD: "YYYY-MM-DD"}

    _repr_medium = {MDY: "MMM DD, YYYY",
                    DMY: "DD MMM, YYYY",
                    YMD: "YYYY MMM DD"}
    _repr_long = {MDY: "MMMM DD., YYYY",
                  DMY: "DD MMMM, YYYY",
                  YMD: "YYYY. MMMM. DD."}

    _repr_email = {MDY: "%m/%d/%Y",
                   DMY: "%d/%m/%Y",
                   YMD: "%Y-%m-%d"}

    @classmethod
    def html_select(cls):
        return [(f, cls._repr_short[f]) for f in cls.available_formats]

    @classmethod
    def get_email_format(cls, code):
        return cls._repr_email[code] if code in cls.available_formats else None

    @classmethod
    def get_format_by_code(cls, code):
        return cls._repr_short[code] if code in cls.available_formats else None

    @classmethod
    def get_momentjs_formats_by_code(cls, code):
        return {
            'short': cls._repr_short[code] if code in cls.available_formats else None,
            'medium': cls._repr_medium[code] if code in cls.available_formats else None,
            'long': cls._repr_long[code] if code in cls.available_formats else None,
        }


def format_datetime2(dt2, format='medium', locale=LC_TIME):
    return format_datetime(dt2.datetime, format=format, locale=locale, tzinfo=dt2.datetime.tzinfo)


def format_naive_isoformat(dt):
    format_str = "{year:0>4}-{month:0>2}-{day:0>2}T{hour:0>2}:{min:0>2}:{sec:0>2}.{microsec:0>6}"
    if isinstance(dt, Datetime2):
        _dt = dt.naive()
    elif isinstance(dt, datetime):
        _dt = dt

    return format_str.format(
        year=_dt.year,
        month=_dt.month,
        day=_dt.day,
        hour=_dt.hour,
        min=_dt.minute,
        sec=_dt.second,
        microsec=_dt.microsecond)


def timezone_as_offset(timezone_str=None):
    """ UTC -> +00:00
        Europe/Budapest -> +01:00
    """
    if timezone_str is not None:
        a = datetime.now(pytz.timezone(timezone_str)).strftime('%z')
        return "{0}:{1}".format(a[0:3], a[3:])
    return "+00:00"


__all__ = [
    'timezones',
    'Datetime2',
    'Date2',
    'DateFormat',
    'timedelta',
    'format_datetime2',
    'timezone_as_offset',
    'format_naive_isoformat',
]
