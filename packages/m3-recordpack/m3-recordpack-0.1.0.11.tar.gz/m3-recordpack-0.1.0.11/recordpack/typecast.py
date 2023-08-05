# coding: utf-8

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

import decimal
import datetime
import json

#------------------------------------------------------------------------------
# Metadata
#------------------------------------------------------------------------------

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


#------------------------------------------------------------------------------
# Typecast implementation
#------------------------------------------------------------------------------

DATETIME_FORMATS = (
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%d %H:%M:%S',
    '%d.%m.%Y %H:%M:%S',
    '%Y-%m-%dT%H:%M',
    '%Y-%m-%d %H:%M',
    '%d.%m.%Y %H:%M',
)


DATE_FORMATS = (
    '%Y-%m-%d',
    '%d.%m.%Y',
    '%m/%d/%Y',
)


def cast_to_datetime(raw, formats=DATETIME_FORMATS):
    return _date_parser(raw, formats)


def cast_to_date(raw, formats=DATE_FORMATS+DATETIME_FORMATS):
    u"""
        datetime - это тоже date. Поэтому если мы передали строку в более
        точном формате - то не валимся, а обрезаем до даты.
    """
    dt = _date_parser(raw, formats)
    return datetime.datetime(dt.year, dt.month, dt.day)


def cast_to_time(raw):
    formats = (
        '%H:%M:%S',
        '%H:%M',
    )
    return _date_parser(raw, formats)


def _date_parser(raw, formats, fallback_parser=None):
    for fmt in formats:
        try:
            converted = datetime.datetime.strptime(raw, fmt)
        except ValueError:
            pass
        else:
            return converted
    else:
        raise ValueError((
            u"Time data '{data!r}' does not match any of known formats:"
            u"\n{formats}"
        ).format(
            data=raw,
            formats='\n'.join(formats))
        )


def typecast(raw, type_, custom_cast=None):
    u""" Приведение данных к определенному типу.

    :param raw: сырые данные
    :param type_: тип приведения
    :param dict custom_cast: позволяется переопредилить порядок приведения,
        в качестве ключа выступает класс типа (:class:`int`, :class:`str`,
        :class:`bool` и т.д), в качестве значение callable с одним аргументом

    :return: значение приведенное к *type_*

    :raise: ValueError, TypeError

    """
    raw = unicode(raw)
    if type_ != basestring:
        raw = raw.strip()
    custom_cast = custom_cast or {}
    cast_map = dict(CAST_MAP, **custom_cast)
    cast = cast_map.get(type_)
    if cast is None:
        raise ValueError("Type converter to '%s' is not defined" % repr(type_))
    return cast(raw)


def mute_typecast(raw, _type, custom_cast=None, default=None):
    u""" Тихое приведение данных к определенному типу.

    Имеет тот же функционал, что и :func:`typecast`, но в случае
    возникновения исключения возвращает *default*.

    """
    try:
        converted = typecast(raw, _type, custom_cast)
    finally:
        return locals().get('converted', default)


CAST_MAP = {
    int: int,
    float: float,
    bool: lambda x: x.lower() in ('true', '1', 'on'),
    decimal.Decimal: lambda x: decimal.Decimal(x),
    basestring: unicode,
    datetime.datetime: cast_to_datetime,
    datetime.date: cast_to_date,
    datetime.time: cast_to_time,
    object: json.loads
}
