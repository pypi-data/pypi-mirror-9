# coding: utf-8

#------------------------------------------------------------------------------
# Metadata
#------------------------------------------------------------------------------

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


#------------------------------------------------------------------------------
# Exception classes
#------------------------------------------------------------------------------

class ProviderException(Exception):
    u""" Ошибка провайдера данных.

    Базовое исключение для всех ошибок провайдера данных.

    """
    def __init__(self, source=None, field=None, key=None):
        self.source = source 
        self.field = field
        self.key = key
        self._message_tpl = '@source={source} @field={field} @key={key}'
        super(ProviderException, self).__init__(self._build_message())

    def _build_message(self):
        message = ''
        if self.source and self.field and self.key:
            try:
                source_name = self.source.__name__
            except AttributeError:
                source_name = self.source.__class__.__name__
            message = self._message_tpl.format(
                source=source_name,
                field=self.field,
                key=self.key)
        return message


class ObjectDoesNotExists(ProviderException):
    u""" Запись не существует.

    Возникает если не удалось найти запись по фильтру.

    """
    pass


class MultipleObjects(ProviderException):
    u""" Множественные данные вместо единичной записи.

    Возникает если по фильтру было получено больше одной записи.

    """
    pass
