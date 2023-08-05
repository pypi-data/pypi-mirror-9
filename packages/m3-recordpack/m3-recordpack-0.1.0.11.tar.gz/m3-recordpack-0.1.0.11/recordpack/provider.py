# coding: utf-8

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from abc import ABCMeta, abstractmethod
from itertools import imap, ifilter
from operator import itemgetter

# 3rdparty
from m3.actions import OperationResult
from django.db.models import Count, Sum
from django.utils.translation import ugettext as _
from m3.db import ObjectState

# Recordpack
from .be import BE
from .exceptions import (ObjectDoesNotExists, MultipleObjects)
from .helpers import init_component
from .proxy import BaseProxy
from . import signals

#------------------------------------------------------------------------------
# Metadata
#------------------------------------------------------------------------------

__author__ = 'Andrey Torsunov'
__contact__ = 'torsunov@bars-open.com'
__docformat__ = 'restructuredtext'

#------------------------------------------------------------------------------
# Constants
#------------------------------------------------------------------------------

SORT_ASC = 'ASC'
SORT_DESC = 'DESC'


#------------------------------------------------------------------------------
# Provider classes
#------------------------------------------------------------------------------

class QueryObject(object):
    u""" Унифицированный интерфейс запросов.

    Класс призванный унифицировать интерфес запросов для разных ORM,
    чтобы работу с данными можно было разнести по разным классам

    """
    def __init__(self, **kwargs):
        #: Дата начала периода выборки
        self.begin = None

        #: Дата окончания периода выборки
        self.end = None

        #: Выражение :class:`~.be.BooleanExpression`
        self.filter = None

        #: Выражение :class:`~.be.BooleanExpression`
        #: Фильтры для поиска (выделены для того, чтобы отличать
        #: колоночные фильтры, от других фильтров, т.к. в случае
        #: с деревом это очень критично)
        self.quick_filter = None

        #: Использовать стандартный менеджер 
        #: :class:`~django.db.models.Manager` или кастомный
        self.from_all = False

        #: Порядок сортировки: 
        #: `['field_a', '-field_b', 'field_c', ..]`
        self.sorting = []

        #: Cвязанные объекты (будут добавлены как select_related)
        self.related = []

        #: Описание итогов в формате:
        #: `{'field': 'aggregate_operation', ..}`
        self.totals = {}

        #: Контекст выполнения (:class:`~m3.actions.context.ActionContext`),
        #: будет передан всем прокси-объектам
        self.context = None

        init_component(self, **kwargs)


class BaseRecordProvider(object):
    u""" Базовый абстрактный класс провайдера данных. """
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        #: Источник данных
        self.data_source = None
        init_component(self, **kwargs)

    @abstractmethod
    def new_record(self, **kwargs):
        u""" Создать запись по переданным данным. """

    @abstractmethod
    def get_record(self, key, query_object):
        u""" Получить одну запись по ключевым реквизитам. """

    @abstractmethod
    def get_records(self, query_object):
        u""" Получить список записей по запрашиваемым параметрам. """

    @abstractmethod
    def validate(self, obj):
        u""" Проверка записи перед сохранением. """

    @abstractmethod
    def save(self, obj):
        u""" Сохранение записи. """

    @abstractmethod
    def delete_record(self, obj):
        u""" Удаление записи. """


class DjangoModelProvider(BaseRecordProvider):
    u""" Базовый провайдер для моделей Django. """
    
    def __init__(self, data_source, key_field='id', related=None):
        super(DjangoModelProvider, self).__init__()
        
        #: Источник данных.
        self.data_source = data_source
        
        #: Поле модели в :attr:`data_source`, которое является 
        #: первичным ключом.
        self.key_field = key_field
        
        #: Связные модели, логика та что и у :meth:`QuerySet.select_related`
        self.related = related
        
        #: Агрегаторы данных для итоговой строки
        self.aggregators = {
            'sum': _aggregate_sum,
            'count': _aggregate_count,
        }

    def _create_filter_conditions(self, filter_):
        u""" Получение фильтра для модели по переданному выражению
        фильтра (BE).
        """
        filters = filter_.to_q() if isinstance(filter_, BE) else None
        return filters

    def _create_sort_for_field(self, field_name, direction):
        u""" Определение порядка сортировки полей.

        Определяет как нужно фильтровать конкретное поле *field_name*
        в направлении *direction*.

        :return: список с фильтруемыми полями, в зависимости от
            конкретной ORM. Список необходим, т.к. фильтрация может
            происходить по вычисляемому полю, соответственно его
            придется развернуть на составляющие поля.
        :rtype: :class:`list`

        """
        if direction == SORT_DESC:
            field_name = '-' + field_name
        elif direction != SORT_ASC:
            raise TypeError('Unknown sort direction {}'.format(direction))
        return [field_name]

    def _create_sort_conditions(self, sorting):
        u"""
        Формирование списка полей, по которым будет происходить фильтрация.
        Переопределять желательно :meth:`_create_sort_for_field`.
        """
        fields = []
        for field, direction in sorting:
            sorting = self._create_sort_for_field(field, direction)
            fields.extend(sorting)
        return fields

    def new_record(self, **kwargs):
        u"""
        Создает новую запись и проставляет в ней значения полей из *kwargs*.
        """
        return self.data_source(**kwargs)

    def get_record(self, key, query_object=None):
        u""" Получение отдельной записи по первичному ключу.

        :param key: значение первичного ключа
        :param query_object: 
        :type query_object: :class:`QueryObject`

        :return: запись найденная по ключу

        :raises ObjectDoesNotExists: если по указанному ключу 
            не найдена запись.
        :raises MultipleObjects: если по указанному ключу найдено
            более одной записи.

        """
        query_object = query_object if query_object else QueryObject()
        try:
            record = self.get_manager(query_object).get((self.key_field, key))
        except self.data_source.DoesNotExist:
            raise ObjectDoesNotExists(
                source=self.data_source,
                field=self.key_field,
                key=key)
        except self.data_source.MultipleObjectsReturned:
            raise MultipleObjects(
                source=self.data_source,
                field=self.key_field,
                key=key)
        else:
            return record

    def _preprocess_record(self, obj, context=None):
        u"""
        Функция позволяет переопределить или дополнить объект,
        который является результатом работы :meth:`get_records`.
        """
        return obj

    def before_query(self, query_object, query):
        return query

    def get_manager(self, query_object):
        u""" Получение менеджера модели.
        
        :param query_object:
        :type query_object: :class:`QueryObject`

        :return: менеджер модели
        :rtype: :class:`~django.db.models.manager.Manager`

        """
        # иногда query_object может быть None
        if getattr(query_object, 'from_all', None) \
                and hasattr(self.data_source, 'objects_all'):
            model_manager = self.data_source.objects_all
        else:
            model_manager = self.data_source.objects

        # [(receiver, result), ...]
        receivers_results = signals.provider_get_manager.send(
            sender=self,
            query_object=query_object,
            manager=model_manager)

        # Фильтрация по второму элементу, если есть хотябы один не None,
        # то он и будет возвращен, в ином случае - значение по-умолчанию.
        extract_manager = itemgetter(1)
        model_manager = next(
            ifilter(None, imap(extract_manager, receivers_results)),
            model_manager)

        return model_manager

    def get_records(self, query_object):
        u"""
        Получение записей, которые удовлетворяют условию из *query_object*.
        
        :param query_object:
        :type query_object: :class:`QueryObject`
        
        :rtype: :class:`dict`

        """
        assert isinstance(query_object, QueryObject)
        data = self.get_manager(query_object).all()

        # Фильтрация
        # -------------------------------------------------------------
        filter_ = self._create_filter_conditions(query_object.filter)
        if filter_:
            data = data.filter(filter_)

        search_filter = self._create_filter_conditions(query_object.quick_filter)
        if search_filter:
            data = data.filter(search_filter)

        # Связанные записи
        # -------------------------------------------------------------
        all_related = self._related_fields(data, query_object)
        if all_related:
            data = data.select_related(*all_related)

        # Сортировка
        # -------------------------------------------------------------
        sorting = self._create_sort_conditions(query_object.sorting)
        if sorting:
            # иначе при сортировке одинаковых значений возвращает разный порядок
            sorting.append('id')
            data = data.order_by(*sorting)

        # Избавление от дубликатов,
        # которые могут появится при наличии множества JOIN'ов
        data = data.distinct()

        # Обработка запроса перед выборкой
        # -------------------------------------------------------------
        data = self.before_query(query_object, data)

        # Срез
        # -------------------------------------------------------------
        total = data.count()
        if query_object.end:
            res_data = data.all()[query_object.begin:query_object.end]
        else:
            res_data = data.all()

        context = query_object.context
        result = [self._preprocess_record(obj, context) for obj in res_data]

        # Подсчет итоговой строки
        # -------------------------------------------------------------
        total_row = self.calc_total(query_object, data)

        if total_row:
            return {'rows': result, 'total': total, 'totalRow': total_row}
        else:
            return {'rows': result, 'total': total}

    def _related_fields(self, data, query_object):
        u""" Возвращает список атрибутов для добавления в select_related. """
        all_related = set()

        if query_object.related:
            all_related.update(query_object.related)

        if self.related:
            all_related.update(self.related)

        if hasattr(data, 'query') and data.query.select_related:
            def fn(d, attr='', res=[]):
                if not d:
                    res.append(attr)
                attr = attr and attr + '___' or ''
                for k, v in d.items():
                    fn(v, attr + k)
                return res
            all_related.update(fn(data.query.select_related))
        return list(all_related)

    def validate(self, obj):
        pass

    def save(self, obj):
        u""" Сохранение записи.

        :param obj: экземпляр :attr:`data_source`

        """
        obj.save()

    def delete_record(self, obj):
        u""" Удаление записи.

        :param obj: экземпляр :attr:`data_source`

        """
        obj.delete()

    def calc_total(self, query_object, results):
        u"""
        Рассчет итоговой строки.

        :param query_object:
        :type query_object: :class:`QueryObject`
        :param results:
        :type results: :class:`django.db.query.QuerySet`

        :rtype: :class:`dict`

        """
        expressions = {}
        total = {}

        for field, aggregation_name in query_object.totals.items():
            if aggregation_name in self.aggregators:
                expr = self.aggregators[aggregation_name](field)
                expressions[field] = expr

        if expressions:
            total = results.model.objects.filter(
                pk__in=results.values_list('pk', flat=True)
            ).aggregate(**expressions)

        return total


class DjangoProxyProvider(DjangoModelProvider):
    u""" Провайдер данных c использованием прокси-объектов.

    Кто-то называет их прокси, кто-то view-model pattern, не суть, 
    главное, что представление строится на основе модели Django.
    Подгрузку и расчет дополнительных данных берет на себя 2 вида прокси:
    * :attr:`card_proxy` - данные для формы редактирования,
    * :attr:`list_proxy` - данные для списка объектов.

    :attr:`card_proxy` может выполнять сохранение, проверку и удаление 
    вместо провайдера, если у него определены соответствующие методы.

    Если какой-либо из прокси классов не задан, то будут отрабатывать методы
    родителя.

    """

    def __init__(self, card_proxy=None, list_proxy=None, *a, **k):
        super(DjangoProxyProvider, self).__init__(*a, **k)
        self.card_proxy = card_proxy
        self.list_proxy = list_proxy

    def _proxy_card_factory(self, obj, context=None):
        u"""
        Позволяет переопределить построение прокси для формы.
        """
        proxy = self.card_proxy(root=obj, context=context)
        proxy.load(obj)
        return proxy

    def _proxy_list_factory(self, obj, context=None):
        u"""
        Позволяет переопределить построение прокси для списка.
        """
        proxy = self.list_proxy(root=obj, context=context)
        proxy.load(obj)
        return proxy

    def new_record(self, **kwargs):
        u"""
        Возвращает новый экземпляр прокси.
        """
        context = kwargs.pop('context', None)
        obj = super(DjangoProxyProvider, self).new_record(**kwargs)
        if self.card_proxy is not None:
            return self._proxy_card_factory(obj, context=context)
        return obj

    def get_record(self, key, query_object=None):
        u"""
        Получает экземпляр прокси, построенный по модели Django.
        """
        obj = super(DjangoProxyProvider, self).get_record(key, query_object)
        if self.card_proxy is not None:
            context = query_object.context if query_object else None
            return self._proxy_card_factory(obj, context=context)
        return obj

    def _preprocess_record(self, obj, context=None):
        u"""
        Переопределяет возвращаемый провайдером класс на прокси объект.
        """
        if self.list_proxy is not None:
            return self._proxy_list_factory(obj, context=context)
        return obj

    def validate(self, obj):
        u"""
        Проверка сначала в прокси, затем если все хорошо в провайдере.
        Вызывается из вне.
        """
        if self.card_proxy and isinstance(obj, self.card_proxy):
            obj.associate()
            result = obj.validate()
            if result:
                return result
        else:
            return super(DjangoProxyProvider, self).validate(obj)

    def save(self, obj):
        u"""
        Делегирует сохраниние в прокси, если у него есть метод `save`.
        """
        if self.card_proxy and isinstance(obj, self.card_proxy):
            if hasattr(self.card_proxy, 'save') and callable(self.card_proxy.save):
                return obj.save()
            else:
                return obj._root.save()
        else:
            return super(DjangoProxyProvider, self).save(obj)

    def delete_record(self, obj):
        u"""
        Делегирует удаление в прокси, если у него есть метод `delete`.
        """
        if self.card_proxy and isinstance(obj, self.card_proxy):
            if hasattr(self.card_proxy, 'delete') and callable(self.card_proxy.delete):
                return obj.delete()
            else:
                return super(DjangoProxyProvider, self).delete_record(obj._root)
        else:
            return super(DjangoProxyProvider, self).delete_record(obj)


class ObjectListProvider(BaseRecordProvider):
    u"""
    Базовый провайдер для списка объектов.
    """
    def __init__(self, data_source, object_class, key_field='id'):
        super(ObjectListProvider, self).__init__()
        self.data_source = data_source
        self.key_field = key_field
        self.object_class = object_class

    def get_data(self):
        if callable(self.data_source):
            return self.data_source()
        else:
            return self.data_source

    def new_record(self, **kwargs):
        u"""
        Создает новую запись и проставляет в ней значения полей из kwargs.
        """
        return self.object_class(**kwargs)

    def get_record(self, key, query_object=None):
        u"""
        Получение отдельной записи по первичному ключу.
        """
        for rec in self.get_data():
            id_ = getattr(rec, self.key_field)
            if id_ == key:
                return rec
        else:
            raise ObjectDoesNotExists

    def _preprocess_record(self, obj, context=None):
        u"""
        Функция позволяет переопределить или дополнить объект,
        который является результатом работы :meth:`get_records`
        """
        if self.object_class is not None:
            return self.object_class(obj, context=context)
        return obj

    def get_records(self, query_object):
        u"""
        Получение записей, которые удовлетворяют условию из query_object
        """
        assert isinstance(query_object, QueryObject)
        data = self.get_data()
        query_filter = query_object.filter
        quick_filter = query_object.quick_filter

        # Фильтрация
        # -------------------------------------------------------------
        intermediate = []
        filtered_data = data[:]

        for filter_ in (query_filter, quick_filter):
            if isinstance(filter_, BE):
                for rec in data:
                    found = filter_.to_bool(
                        left_callback=lambda fld: getattr(rec, fld))
                    if found:
                        intermediate.append(rec)
                filtered_data, intermediate = intermediate, []

        # Сортировка
        # -------------------------------------------------------------
        sorted_data = filtered_data
        for field, direction in query_object.sorting:
            sorted_data = sorted(
                filtered_data,
                key=lambda rec: getattr(rec, field),
                reverse=(direction == SORT_DESC))

        # Срез
        # -------------------------------------------------------------
        total = len(sorted_data)
        if query_object.end:
            res_data = sorted_data[query_object.begin:query_object.end]
        else:
            res_data = sorted_data

        context = query_object.context
        result = [self._preprocess_record(obj, context) for obj in res_data]
        total_row = self.calc_total(query_object, sorted_data)

        if total_row:
            return {'rows': result, 'total': total, 'totalRow': total_row}
        else:
            return {'rows': result, 'total': total}

    def validate(self, obj):
        if hasattr(obj, 'associate') and callable(obj.associate):
            obj.associate()
        if hasattr(obj, 'validate') and callable(obj.validate):
            return obj.validate()

    def save(self, obj):
        data = self.get_data()
        if not obj in data:
            data.append(obj)

    def delete_record(self, obj):
        data = self.get_data()
        data.remove(obj)

    def calc_total(self, query_object, results):
        u"""
        Рассчет итоговых полей.
        """
        result = {}
        for item in results:
            self.calc_total_item(query_object, item, result)
        return result

    def calc_total_item(self, query_object, item, total):
        u"""
        Обновляем итог по элементу.
        """
        for key, operation in query_object.totals.items():
            if hasattr(item, key):
                if key not in total:
                    total[key] = 0
                if operation == 'count':
                    total[key] += 1
                if operation == 'sum':
                    total[key] += getattr(item, key)


#------------------------------------------------------------------------------
# Aggregators
#------------------------------------------------------------------------------

def _aggregate_sum(field_name):
    return Sum(field_name)

def _aggregate_count(field_name):
    return Count(field_name)


#------------------------------------------------------------------------------
# Decorators
#------------------------------------------------------------------------------

class BaseDataProviderExtender(BaseRecordProvider):
    """
    Объект-декоратор, обертывающий некоторые функции у провайдера
    """
    def __init__(self, target_class):
        super(BaseDataProviderExtender, self).__init__()
        self.target_class = target_class

    def __getattribute__(self, attr):
        # переопределяем получение атрибутов, чтобы обращение было сразу к targer_class
        # за некоторым исключением
        if attr in ['new_record', 'get_record', 'get_records',
                    'validate', 'save', 'delete_record', 'target_class']:
            return super(BaseDataProviderExtender, self).__getattribute__(attr)
        else:
            return getattr(self.target_class, attr)

    def new_record(self, **kwargs):
        return self.target_class.new_record(**kwargs)

    def get_record(self, key, query_object=None):
        return self.target_class.get_record(key)

    def get_records(self, query_object):
        return self.target_class.get_records(query_object)

    def validate(self, obj):
        return self.target_class.validate(obj)

    def save(self, obj):
        return self.target_class.save(obj)

    def delete_record(self, obj):
        return self.target_class.delete_record(obj)
