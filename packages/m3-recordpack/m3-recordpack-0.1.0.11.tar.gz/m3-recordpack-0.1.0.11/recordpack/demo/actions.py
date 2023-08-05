# coding: utf-8

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
import datetime

# Recordpack
from recordpack import recordpack
from recordpack.provider import DjangoProxyProvider
from recordpack.be import BE
from recordpack.typecast import cast_to_date

# Demo
import ui
import column_filter
from proxy import PersonListProxy
from models import Person

#------------------------------------------------------------------------------
# Demonstrative action packs
#------------------------------------------------------------------------------

class PersonPack(recordpack.BaseRecordListPack):
    u"""
    Recordpack для модели Person.
    """
    url = '/person'
    title = u'Физические лица'
    title_plural = u'Физические лица'

    edit_window = new_window = ui.PersonEditWindow
    list_window = ui.PersonListWindow

    provider = DjangoProxyProvider(
        data_source=Person,
        list_proxy=PersonListProxy)

    quick_filters = {
        'sname': {'control': {'xtype': 'textfield'}},
        'fname': {'control': {'xtype': 'textfield'}},
        'mname': {'control': {'xtype': 'textfield'}},
        'birthday': {'expr': column_filter.person_birthday},
        'gender': {'expr': column_filter.person_gender},
    }

    sorting = ('sname', 'fname', 'mname', 'birthday', 'gender')
