# coding: utf-8

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
import datetime

# 3rdparty
from django.db import models

# Recordpack
from recordpack.be import BE
from recordpack.typecast import mute_typecast


#------------------------------------------------------------------------------
# Helpers functions
#------------------------------------------------------------------------------

def person_birthday(date_string):
    date_string = date_string.strip()
    code2oper = (
        ('<=', BE.LE),
        ('>=', BE.GE),
        ('<', BE.LT),
        ('>', BE.GT),
        ('', BE.EQ),
    )
    for oper_code, oper in code2oper:
        if date_string.startswith(oper_code):
            date_string = date_string.lstrip(oper_code)
            birthday = mute_typecast(date_string, datetime.date)
            return birthday and BE('birthday', oper, birthday) or None


def person_gender(gender_string):
    _filter = None
    person_model = models.get_model('demo', 'Person')
    for index, gender in person_model.GENDERS_LIST:
        if gender_string in gender:
            _filter |= BE('gender', BE.EQ, index)
    return _filter