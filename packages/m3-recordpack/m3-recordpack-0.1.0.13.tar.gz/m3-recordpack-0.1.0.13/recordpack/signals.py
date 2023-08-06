# coding: utf-8

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# 3rdparty
from django.dispatch import Signal

#------------------------------------------------------------------------------
# Metadata
#------------------------------------------------------------------------------

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'

#------------------------------------------------------------------------------
# Signals
#------------------------------------------------------------------------------


# Recordpack
# ---------------------------------------------------------------------

#: Сигнал создания журнального окна, вызывается в:
#: :meth:`~recordpack.recordpack.BaseRecordListPack.request_list_window`
base_record_list_pack_after_get_list_window = Signal(
    providing_args=['instance', 'request', 'context', 'window'])

#: Сигнал создания окна выбора записи, вызывается в:
#: :meth:`~recordpack.recordpack.BaseRecordListPack.request_select_window`
base_record_list_pack_after_get_select_window = Signal(
    providing_args=['instance', 'request', 'context', 'window'])

#: Сигнал создания окна редактирования, вызывается в:
#: :meth:`~recordpack.recordpack.BaseRecordPack.request_edit_window`
base_record_pack_after_get_edit_window = Signal(
    providing_args=['instance', 'request', 'context', 'record', 'window',
                    'is_new'])

#: Сигнал перед извлечением записей, вызывается в:
#: :meth:`~recordpack.recordpack.BaseRecordPack.request_rows`
base_record_pack_before_get_rows = Signal(
    providing_args=['instance', 'request', 'context', 'query'])

#: Сигнал после извлечения записей, вызывается в:
#: :meth:`~recordpack.recordpack.BaseRecordPack.request_rows`
base_record_pack_after_get_rows = Signal(
    providing_args=['instance', 'request', 'context', 'query', 'rows'])


# Providers
# ---------------------------------------------------------------------

#: Сигнал определения менеджера, вызывается в:
#: :meth:`~recordpack.provider.DjangoModelProvider.get_manager`
provider_get_manager = Signal(providing_args=['query_object', 'manager'])
