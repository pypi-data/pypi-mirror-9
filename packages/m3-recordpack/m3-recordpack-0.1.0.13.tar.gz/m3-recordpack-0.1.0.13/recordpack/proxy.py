# coding: utf-8

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from abc import ABCMeta
from operator import attrgetter

# 3rdparty
from django.db.models import Model as DjangoModel

#------------------------------------------------------------------------------
# Metadata
#------------------------------------------------------------------------------

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'


#------------------------------------------------------------------------------
# Proxy classes
#------------------------------------------------------------------------------

class BaseProxy(object):
    u""" Базовый прокси класс для объектов отвечающих за
    представление сущности в UI.

    Может перехватывать у провайдера ``save`` и ``delete``, если одноименные
    методы определены в дочернем классе.

    Жизненный цикл прокси:

    * ``Создание > Заполнение данными > Привязка к форме > JSON``
    * ``JSON > Привязка из формы > Ассоциация > Проверка > Сохранение``

    .. note::
        protected и private атрибуты не подлежат сериализации в JSON

    """
    __metaclass__ = ABCMeta

    model_meta_fields_attr = 'local_fields'
    _models_field_cache = {}

    def __init__(self, root, context=None):
        #: Корневой объект сущности, который может тянуть за собой
        #: остальные подчиненные объекты.
        self._root = root
        #: Перемещенные поля от :attr:`_root` и обратно
        self._transferred_fields = []
        #: Контекст создания объекта, заполняется при создании в провайдере
        self._context = context

    def load(self, root):
        u"""
        Вызывается провайдером, для загрузки данных из полей root в атрибуты прокси.
        В процессе этого могут быть расчитаны вычисляемые поля.

        :param root: экземпляр записи модели
        :type root: :class:`django.db.models.Model`

        """
        pass

    def associate(self):
        """
        Метод вызывается после привязки данных к прокси. Как правило в процессе сохранения.
        Может понадобиться, например, если нужно перенести какие-то атрибуты их прокси в модель,
        либо просчитать значения атрибутов.
        Ничего не возвращает. Не использовать для валидации!
        """
        pass

    def validate(self):
        """
        Метод используется для проверки данных перед сохранением.
        Если проверка прошла успешно, то не возвращаем ничего. Иначе результат
        вернется прямо в экшен.
        """
        pass

    #--------------------------------------------------------------------------
    # Перемещение атрибутов
    #--------------------------------------------------------------------------

    def from_root(self):
        u""" Перенос значений всех полей и json методов в атрибуты класса. """
        self.transfer_fields(self._root, self)

    def to_root(self):
        """ Перенос значений полей из прокси обратно в корневой объект.

        Переносятся только поля, которые изначально были перенесены с
        помощью :meth:`from_root` и сохранены в :attr:`_transferred_fields`.

        """
        for attr in self._transferred_fields:
            value = getattr(self, attr)
            setattr(self._root, attr, value)

    def transfer_field_from_root(self):
        u"""
        .. deprecated:: 
           Рекомендуется использовать :meth:`from_root`.
        """
        self.from_root()

    def transfer_fields_back_to_root(self):
        """
        .. deprecated:: 
           Рекомендуется использовать :meth:`to_root`.
        """
        self.to_root()

    def transfer_fields(self, src_obj, dst_obj, exclude=()):
        """
        Перенос значений всех полей *src_obj* и json методов в
        атрибуты объкта *dst_obj*

        :param src_obj: объект источник
        :param dst_obj: объект приемник
        :param tuple exclude: перечисление полей, которые
            следует исключить при перемещении

        """

        fields = self._get_model_fields(src_obj)

        if fields:
            for attr in fields:
                if attr in exclude:
                    continue

                value = getattr(src_obj, attr)
                setattr(dst_obj, attr, value)
                self._transferred_fields.append(attr)

        for attr in src_obj.__dict__.keys():
            if not attr.startswith('_'):
                attr_value = getattr(src_obj, attr)
                if hasattr(attr_value, 'json_encode') and callable(attr_value):
                    value = attr_value()
                    setattr(dst_obj, attr, value)
                elif not fields:
                    setattr(dst_obj, attr, attr_value)

    #--------------------------------------------------------------------------
    # Служебные методы
    #--------------------------------------------------------------------------

    @classmethod
    def _get_model_fields(cls, src_obj):
        """
        Получение имен полей модели (использует кеширование)
        """
        result = None
        if isinstance(src_obj, DjangoModel):
            result = cls._models_field_cache.get(src_obj.__class__)
            if result is None:
                result = cls._models_field_cache[src_obj.__class__] = map(
                    attrgetter('attname'),
                    getattr(src_obj._meta, cls.model_meta_fields_attr, []))
        return result

    #--------------------------------------------------------------------------
    # Свойства
    #--------------------------------------------------------------------------

    @property
    def context(self):
        u""" Получение контекста запроса, в котором создан этот прокси. """
        return self._context


class BaseStateProxy(BaseProxy):
    u"""
    Автоматически извлекает поля с состоянием для работы с формой
    RecordEditWindow. Перед сохранением присваивает значения полей
    корневой модели.
    """
    def __init__(self, root, context=None):
        super(BaseStateProxy, self).__init__(root, context)
        self.id = root.id
        self.state = root.state
        self.begin = root.begin
        self.end = root.end
        self.version = root.version

    def associate(self):
        super(BaseStateProxy, self).associate()
        self._root.state = self.state
        self._root.begin = self.begin
        self._root.end = self.end
        self._root.version = self.version

    #--------------------------------------------------------------------------
    # Заглушки
    #--------------------------------------------------------------------------

    def do_lock(self):
        return self._root.do_lock()
