# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)


from datetime import datetime
from json import dumps
from copy import copy, deepcopy
from unittest import TestCase, main, TestLoader, TextTestRunner
from os import getcwd
from unicum import DecoratorFactory, SingletonObject, FactoryObject, ObjectList, \
    LinkedObject, PersistentObject, AttributeList, VisibleObject, VisibleAttributeList
from unicum.datarange import DataRange
from unicum.olddatarange import IndexedList


class TestDummy(object):
    pass


class CacheTest(TestCase):
    def setUp(self):
        self.cache = DecoratorFactory()

        class UnnamedObject(object):
            def __init__(self, *args, **kargs):
                pass

            def __str__(self):
                return self.__class__.__name__

            def to_serializable(self, level=0):
                return str(self)

        class DayCount(UnnamedObject):
            pass

        self.DayCount = DayCount

    def test_NamedObject(self):
        # - test NamedObject -

        @self.cache.by_key
        class NamedObject(object):
            def __init__(self, name='last'):
                self.name = name

        first = NamedObject('First')
        self.cache['Second'] = first
        second = NamedObject('second')
        self.assertEqual(first, second)

        third = NamedObject('Third')
        self.assertNotEqual(first, third)
        self.assertEqual(third, NamedObject('third'))

        self.cache.pop('third')
        self.assertNotEqual(third, NamedObject('third'))

        self.cache['Forth'] = NamedObject('first')
        forth = NamedObject('Forth')
        self.assertEqual(NamedObject('first'), forth)
        self.assertEqual(second, NamedObject('forth'))

        self.cache['Fifth'] = NamedObject('first')
        self.assertEqual(second, NamedObject('fifth'))
        self.cache.pop('FIFTH')
        self.assertNotIn('fifth', self.cache)

        last = NamedObject()
        self.assertNotEqual(last, NamedObject())
        self.assertNotIn('NamedObject', self.cache)

        name_objects = DecoratorFactory(self.cache.cache, NamedObject)
        with self.assertRaises(KeyError):
            name_objects()

    def test_UnnamedObject(self):
        # - test UnnamedObject -

        @self.cache.by_class_name
        class ActAct(self.DayCount):
            pass

        @self.cache.by_class_name
        class Thirty360(self.DayCount):
            pass

        Thirty360()
        self.cache['Act/Act'] = ActAct()
        self.cache['Act_Act'] = ActAct()
        self.assertEqual(self.cache['Act/ACT'], ActAct())
        self.assertEqual(self.cache['ACTACT'], self.cache['ACT/act'])

        day_count = DecoratorFactory(self.cache.cache, self.DayCount, 'ActAct')
        self.assertEqual(day_count(), ActAct())
        self.assertEqual(day_count('actact'), ActAct())

        self.assertEqual(ActAct().to_serializable(), 'ActAct')
        self.assertEqual(self.cache['Act/ACT'].to_serializable(), 'ActAct')


class SingletonTest(TestCase):
    def setUp(self):
        class SingeltonDummy(TestDummy, SingletonObject):
            pass

        self.Constant = SingeltonDummy

    def test_singleton(self):
        c = self.Constant()
        d = self.Constant()
        self.assertEqual(c, d)


class FactoryTest(TestCase):
    def setUp(self):
        class Currency(FactoryObject):
            __factory = dict()

            def __new__(cls, *args, **kwargs):
                if not args:
                    return super(Currency, cls).__new__(cls, cls.__name__)
                else:
                    return super(Currency, cls).__new__(cls, *args)

            def __init__(self, name=None):
                super(Currency, self).__init__(name)
                self._vp_ = self.__class__.__name__

        self.Currency = Currency

        class EUR(Currency):
            @property
            def vp(self):
                return self._vp_

        self.EUR = EUR

        class USD(Currency):
            @property
            def vp(self):
                return self._vp_

        self.USD = USD

        class CurrencyList(ObjectList):
            def __init__(self, iterable=None):
                super(CurrencyList, self).__init__(iterable, Currency)

            def __add__(self, other):
                return CurrencyList(super(CurrencyList, self).__add__(other))

            def __iadd__(self, other):
                return CurrencyList(super(CurrencyList, self).__iadd__(other))

        self.CurrencyList = CurrencyList

        class Interpolation(FactoryObject):
            __factory = dict()

        class FactoryDummy(TestDummy, Interpolation):
            pass

        self.FactoryDummy = FactoryDummy

        class AnotherFactoryDummy(TestDummy, Interpolation):
            pass

        self.AnotherFactoryDummy = AnotherFactoryDummy

        class FactoryDummySubClass(AnotherFactoryDummy):
            pass

        self.FactoryDummySubClass = FactoryDummySubClass

    def test_first_factory(self):
        e = self.FactoryDummy().register()
        f = self.AnotherFactoryDummy().register()
        n = self.FactoryDummySubClass().register()
        g = n.__class__(str(f))
        self.assertTrue(e is not f)
        self.assertTrue(g is f)

    def test_second_factory(self):
        # test FactoryObject
        eur = self.EUR().register()
        self.EUR().register('eur')

        usd = self.USD().register()
        self.assertTrue(eur is not usd)

        neur = self.USD('EUR')
        self.assertTrue(eur is neur)
        self.assertTrue(self.USD('EUR').vp is 'EUR')
        self.assertTrue(self.USD('USD').vp is 'USD')

        fEUR = self.Currency('EUR')
        feur = self.Currency('eur')
        self.assertTrue(type(eur) is type(fEUR))
        self.assertTrue(eur is feur)
        self.assertTrue(fEUR is feur)

        for x, y in zip(self.EUR.values(), self.USD.values()):
            self.assertTrue(x is y)

        for ek, (k, v), ev in zip(self.EUR.keys(), self.USD.items(), self.Currency.values()):
            self.assertTrue(ek is k)
            self.assertTrue(v is ev)

        self.Currency('EUR').remove()
        self.assertTrue(len(self.EUR.items()) is 1)
        self.assertTrue(self.EUR.values()[0] is usd)
        self.assertTrue(usd in self.Currency.values())
        self.assertTrue(eur not in self.Currency.values())

        # NamedObject -> create item by self.__class__(obj_name)
        # NamedObject by SingletonObject
        # NamedObject from FactoryObject

        # Idempotent, Strong or SingletonNamedObject
        # e.g. __factory, singleton subs
        ccy = self.EUR().register()
        self.assertTrue(ccy == ccy.__class__(ccy.to_serializable()))
        self.assertTrue(ccy == ccy.__class__(ccy.__str__()))
        self.assertTrue(ccy == ccy.__class__(ccy))
        self.assertTrue(ccy == self.Currency(ccy))

        # Equivalent, Weak or SimpleNamedObject
        # e.g. BusinessDate, BusinessPeriod
        ccy = self.EUR()
        self.assertTrue(str(ccy) is str(ccy.__class__(ccy.__str__())))
        self.assertTrue(str(ccy) is str(ccy.__class__(ccy.__str__())))

    def test_register(self):
        # test FactoryObject
        eur = self.EUR().register()
        self.assertTrue('EUR' in self.EUR.keys())

        names = 'eur', 'Eur', 'EURO', 'euro'
        self.EUR().register(*names)
        keys = self.EUR.keys()
        for n in names:
            self.assertTrue(n in keys)

    def test_mixed(self):
        usd = self.USD().register()
        const = self.FactoryDummy().register()

        self.assertTrue(usd in self.USD.values())
        self.assertTrue(usd not in self.FactoryDummy.values())

        self.assertTrue(const not in self.USD.values())
        self.assertTrue(const in self.FactoryDummy.values())

    def test_objectList(self):
        eur, usd = self.EUR().register(), self.USD().register()
        l = (eur, usd)
        o = ObjectList(l, self.Currency)
        o = self.CurrencyList(o)
        self.assertTrue(o == o.__class__(l))
        self.assertTrue(o == o.__class__(o))
        self.assertTrue(o == o.__class__(o.to_serializable()))

        for x, y in zip(l, o.to_serializable()):
            self.assertTrue(type(y) is str)
            self.assertTrue(str(x) is y)

        const = self.FactoryDummy().register()
        ol = (lambda x: ObjectList(x, object_type=self.Currency))
        self.assertRaises(TypeError, ol, (eur, const))

        eur.register('eur')
        usd.register('usd')

        o[0] = eur
        self.assertTrue(eur in o)
        o.pop(0)
        self.assertTrue(eur not in o)
        o[0] = 'eur'
        self.assertTrue(eur in o)
        o.pop(0)
        o.insert(0, eur)
        self.assertTrue(eur in o)
        o.pop(0)
        o.insert(0, 'eur')
        self.assertTrue(eur in o)
        o.pop(0)
        o.append(eur)
        self.assertTrue(eur in o)
        o.pop(0)
        o.append('eur')
        self.assertTrue(eur in o)
        o.pop(0)
        o.extend([eur])
        self.assertTrue(eur in o)
        o.pop(0)
        o.extend(['eur'])
        self.assertTrue(eur in o)
        o.pop(0)
        o[0:0] = [eur]
        self.assertTrue(eur in o)
        o.pop(0)
        o[0:0] = ['eur']
        self.assertTrue(eur in o)

        b = o + ['eur']
        self.assertTrue(isinstance(b, self.CurrencyList))
        self.assertTrue(eur in b)

        b = ['eur'] + o
        self.assertTrue(not isinstance(b, ObjectList))
        self.assertTrue(eur in b)

    def test_get_item(self):
        eur, usd = self.EUR().register(), self.USD().register()
        l = (eur, usd)
        o = ObjectList(l, self.Currency)
        o = self.CurrencyList(o)
        self.assertEqual(o['EUR'], eur)
        self.assertTrue(eur in o)
        self.assertEqual(o.index(eur), 0)
        self.assertEqual(o.get(eur), eur)
        self.assertEqual(o.get('EUR'), eur)

class MyLO(LinkedObject):
    def __init__(self):
        super(MyLO, self).__init__()
        self.property = LinkedObject()


class YourLO(LinkedObject):
    def __init__(self):
        super(YourLO, self).__init__()
        self.property = 'It is yours.'


class LinkedTest(TestCase):
    def test_object_link(self):
        # test FactoryObject
        # ------------

        m = MyLO()
        n = MyLO()
        self.assertTrue(m.property is not n.property)
        self.assertTrue(len(LinkedObject._get_links()) is 1)
        self.assertTrue(m.property.__class__.__name__ in LinkedObject._get_links())
        self.assertTrue(n.property.__class__.__name__ in LinkedObject._get_links())

        m.property = n.property
        self.assertTrue(m.property is n.property)
        self.assertTrue(len(LinkedObject._get_links()) is 1)
        self.assertTrue(m.property.__class__.__name__ in LinkedObject._get_links())
        self.assertTrue(n.property.__class__.__name__ in LinkedObject._get_links())

        z = YourLO()
        y = YourLO()
        m.property = n.property = y
        self.assertTrue(m.property is y)
        self.assertTrue(m.property is not z)
        self.assertTrue(m.property is n.property)
        self.assertTrue(len(LinkedObject._get_links()) is 1)
        self.assertTrue(m.property.__class__.__name__ in LinkedObject._get_links())
        self.assertTrue(n.property.__class__.__name__ in LinkedObject._get_links())

        z.update_link()
        self.assertTrue(m.property is not y)
        self.assertTrue(m.property is z)
        self.assertTrue(m.property is n.property)
        self.assertTrue(len(LinkedObject._get_links()) is 1)
        self.assertTrue(m.property.__class__.__name__ in LinkedObject._get_links())
        self.assertTrue(n.property.__class__.__name__ in LinkedObject._get_links())


class MyPO(PersistentObject):
    def __init__(self):
        super(MyPO, self).__init__()
        self._my_property_ = 'It is mine.'


class YourPO(PersistentObject):
    def __init__(self):
        super(YourPO, self).__init__()
        self._your_property_ = 'It is yours.'


class PersistentTest(TestCase):
    def test_obj(self):
        p = MyPO()
        self.assertTrue(type(p) is MyPO)
        self.assertTrue(hasattr(p, '_class_'))

    def test_visible(self):
        for a in ['_class_', 'ObjectName']:
            if MyPO._is_visible(a):
                self.assertEqual(a, MyPO._to_visible(a))
            else:
                self.assertEqual(a, MyPO._from_visible(a))
                # print a, MyPO._is_visible(a), MyPO._to_visible(a), MyPO._from_visible(a)

    def test_obj_to_dict(self):
        d = MyPO().to_serializable(all_properties=True)
        self.assertTrue('Class' in d)
        self.assertTrue(d['MyProperty'] == 'It is mine.')

    def test_dict_to_obj(self):
        e = {'Class': 'PersistentObject'}
        self.assertTrue(type(MyPO.from_serializable(e)) is PersistentObject)
        e = {'Class': 'YourPO', 'Module': __name__}
        self.assertTrue(MyPO.from_serializable(e).to_serializable()['Class'] == 'YourPO')

    def test_json(self):
        e = {'Class': 'PersistentObject'}
        j = dumps(e)
        o = PersistentObject.from_json(j)
        self.assertEqual(type(o), PersistentObject)

        e = {'Class': 'YourPO', 'Module': __name__, 'YourProperty': 'It is mine.'}
        j = dumps(e, indent=2, sort_keys=True)
        o = PersistentObject.from_json(j)
        self.assertTrue(type(o) is YourPO)
        self.assertEqual(o.to_json(indent=2), j)
        self.assertEqual(o.to_serializable(), PersistentObject.from_serializable(e).to_serializable())

    def test_modify_obj(self):
        q = MyPO()
        q.modify_object('MyProperty', 'Hello World.')
        self.assertTrue(q._my_property_ == 'Hello World.')
        d = q.to_serializable()
        self.assertTrue(d['MyProperty'] == 'Hello World.')

        # no direct circle assignment
        self.assertRaises(ValueError, q.modify_object, 'MyProperty', q)

    def test_modify_factory_obj(self):
        class MyFactoryObject(FactoryObject):
            pass

        q = MyPO()
        fo = FactoryObject().register()
        fo.register('MyObj')
        mfo = MyFactoryObject().register()

        q._my_property_ = FactoryObject()
        self.assertTrue(q._my_property_ == fo)
        q.modify_object('MyProperty', 'MyFactoryObject')
        self.assertTrue(q._my_property_ == mfo)
        q.modify_object('MyProperty', 'MyObj')
        self.assertTrue(q._my_property_ == fo)
        q.modify_object('MyProperty', MyFactoryObject())
        self.assertTrue(q._my_property_ == mfo)

    def test_attribute_list(self):
        l = MyPO(), YourPO()
        a = AttributeList(l)

        self.assertTrue(a == a.__class__(l))
        self.assertTrue(a == a.__class__(a))

    def test_attribute_list2(self):
        ol = (lambda x: AttributeList(x, object_type=MyPO))
        l = MyPO(), MyPO()
        self.assertTrue(len(ol(l)) == 2)
        l = YourPO(), MyPO()
        self.assertRaises(TypeError, ol, l)

    def test_attribute_list3(self):
        l = YourPO(), MyPO()
        a = AttributeList(l)
        m = MyPO()

        a[0] = m
        self.assertTrue(m in a)
        a.pop(0)
        self.assertTrue(m not in a)

        a.insert(0, m)
        self.assertTrue(m in a)
        a.pop(0)
        self.assertTrue(m not in a)

        a.append(m)
        self.assertTrue(m in a)
        a.pop(-1)
        self.assertTrue(m not in a)

        a.extend([m])
        self.assertTrue(m in a)
        a.pop(-1)
        self.assertTrue(m not in a)

        a[0:0] = [m]
        self.assertTrue(m in a)
        a.pop(0)
        self.assertTrue(m not in a)

        b = a + [m]
        self.assertTrue(isinstance(b, AttributeList))
        self.assertTrue(m in b)

        b = [m] + a
        self.assertTrue(not isinstance(b, AttributeList))
        self.assertTrue(m in b)


class IndexedListTest(TestCase):
    def setUp(self):
        self.values = range(100)
        self.keys = [str(i) for i in self.values]
        self.list = IndexedList(self.keys, self.values)

    def test_list(self):
        indexed_list = IndexedList(self.list)
        for il, org in zip(indexed_list.keys(), self.keys):
            self.assertEqual(il, org)
        for il, org in zip(indexed_list.keys(), self.values):
            self.assertEqual(indexed_list[il], org)
        for il, org in zip(indexed_list.values(), self.values):
            self.assertEqual(il, org)
        for k, v in indexed_list.items():
            self.assertEqual(k, str(v))

        self.assertEqual(indexed_list[2:50], indexed_list['2':'49'])
        self.assertEqual(indexed_list[2:], indexed_list['2':])
        self.assertEqual(indexed_list[:2], indexed_list[:'1'])

        new = ['A', 'B']
        indexed_list['3':'5'] = new
        self.assertEqual(indexed_list[3], new[0])
        self.assertEqual(indexed_list[4], new[1])
        self.assertEqual(indexed_list[3:5], new)

    def test_set(self):
        indexed_list = IndexedList(self.list)
        self.assertEqual(len(indexed_list), 100)

        indexed_list.append(100)
        self.assertEqual(len(indexed_list), 101)
        self.assertEqual(indexed_list[100], 100)

        indexed_list.insert('50', -1)
        self.assertEqual(len(indexed_list), 102)
        self.assertEqual(indexed_list[50], -1)
        self.assertEqual(indexed_list[49], 49)
        self.assertEqual(indexed_list[51], 50)

        indexed_list.extend(['a'], ['b'])
        self.assertEqual(indexed_list.keys()[-1], 'a')
        self.assertEqual(indexed_list[-1], 'b')

        new_il = IndexedList(['c'], ['d'])
        indexed_list.extend(new_il)
        self.assertEqual(indexed_list.keys()[-1], 'c')
        self.assertEqual(indexed_list[-1], 'd')

        new_il = IndexedList(['c'], ['c'])
        l = (lambda x: indexed_list.extend(x))
        self.assertRaises(KeyError, l, new_il)


class DataRangeTest(TestCase):
    def setUp(self):
        h = '', 'A', 'B', 'C', 'D'
        x = 'X', 1, 2, 3, 4
        y = 'Y', 4, 5, 6, 7
        z = 'Z', 7, 8, 9, 10
        self.datarange = DataRange([h, x, y, z])
        pass

    def test_keys(self):
        self.assertEqual(self.datarange.col_keys(), ['A', 'B', 'C', 'D'])
        self.assertEqual(self.datarange.row_keys(), ['X', 'Y', 'Z'])

    def test_get(self):
        self.assertEqual(self.datarange.get(('X', 'A')), 1)
        self.assertEqual(self.datarange.row('X'), [1, 2, 3, 4])
        self.assertEqual(self.datarange.col('D'), [4, 7, 10])
        # self.assertEqual(self.datarange[0][-1], 4)
        self.assertEqual(self.datarange[0, -1], 4)
        # self.assertEqual(self.datarange['X']['C'], 3)
        self.assertEqual(self.datarange['X', 'C'], 3)

    def test_slice(self):
        self.assertEqual(self.datarange[0:2], self.datarange['X':'Y'])
        self.assertEqual(self.datarange[0:1], [[1, 2, 3, 4]])
        self.assertEqual(self.datarange[(0, 1):(2, 3)], [[2, 3], [5, 6]])
        # self.assertEqual([l[1:3] for l in self.datarange[0:2]], [[2, 3], [5, 6]])
        # self.assertEqual([l[1:3] for l in self.datarange['X':'Y']], [[2, 3], [5, 6]])
        # self.assertEqual([l['B':'C'] for l in self.datarange['X':'Y']], [[2, 3], [5, 6]])
        self.assertEqual(self.datarange[('X', 'B'):('Y', 'C')], [[2, 3], [5, 6]])
        self.assertEqual(self.datarange[(None, 'B'):('Y', 'C')], [[2, 3], [5, 6]])
        self.assertEqual(self.datarange[(None, 'B'):('Y', None)], [[2, 3, 4], [5, 6, 7]])

    def test_flatten(self):
        self.assertEqual(DataRange(self.datarange.to_serializable()), self.datarange)
        s = "DataRange([[None, 'A', 'B', 'C', 'D'], ['X', 1, 2, 3, 4], ['Y', 4, 5, 6, 7], ['Z', 7, 8, 9, 10]])"
        self.assertEqual(str(self.datarange), s)

    def test_set(self):
        # self.datarange['X']['C'] = 4
        # self.assertEqual(self.datarange['X']['C'], 4)
        self.datarange['X', 'C'] = 3
        l = self.datarange.__setitem__
        self.assertRaises(KeyError, l, ('U', 'C'), 4)
        self.assertRaises(KeyError, l, ('X', 'X'), 4)

    def test_append(self):
        self.datarange.append('W', range(4))
        l = lambda: self.datarange.row_append('W', range(4))
        self.assertRaises(KeyError, l)
        self.assertEqual(len(self.datarange), 4)
        self.assertEqual(self.datarange.row_keys()[-1], 'W')
        self.assertEqual(self.datarange.row(-1), range(4))

        self.datarange.row_append('U', range(2, 6))
        self.assertEqual(self.datarange.row('U'), range(2, 6))
        self.assertEqual(self.datarange.row(4), range(2, 6))
        self.assertEqual(self.datarange.row(-1), range(2, 6))

        self.datarange.col_append('T', range(5))
        self.assertEqual(self.datarange.col('T'), range(5))
        self.assertEqual(self.datarange.col(4), range(5))
        self.assertEqual(self.datarange.col(-1), range(5))

    def test_copy(self):
        self.assertEqual(self.datarange, copy(self.datarange))
        self.assertEqual(type(self.datarange), type(copy(self.datarange)))
        self.assertEqual(self.datarange, deepcopy(self.datarange))
        self.assertEqual(type(self.datarange), type(deepcopy(self.datarange)))

    def test_transpose(self):
        self.assertEqual(type(list(self.datarange)), list)
        l = [self.datarange.row(r) for r in self.datarange.row_keys()]
        self.assertEqual(self.datarange.item_list, l)
        self.assertEqual(type(self.datarange), type(self.datarange.transpose()))

    def test_pickle(self):
        try:
            import dill as pickle
        except ImportError:
            pass
        else:
            dr = DataRange()
            p = pickle.dumps(dr)
            d = pickle.loads(p)
            self.assertEqual(type(d), DataRange)
            self.assertEqual(dr.to_serializable(), d.to_serializable())

            self.assertEqual(type(self.datarange), DataRange)
            p = pickle.dumps(self.datarange)
            d = pickle.loads(p)
            self.assertEqual(self.datarange, d)


class MyVO(VisibleObject):
    def __init__(self, *args):
        super(MyVO, self).__init__(*args)
        self._none_prop_ = None
        self._str_prop_ = str('my str')
        self._int_prop_ = int(100)
        self._flt_prop_ = float(99.01)
        self._obj_prop_ = VisibleObject('YourVisibleObject')
        self._obj_list_prop_ = ObjectList()
        self._attr_list_prop_ = AttributeList()
        self._data_range_prop_ = DataRange()

    @property
    def none(self):
        return self._none_prop_

    @property
    def str(self):
        return self._str_prop_

    @property
    def int(self):
        return self._int_prop_

    @property
    def flt(self):
        return self._flt_prop_

    @property
    def obj(self):
        return self._obj_prop_

    @property
    def obj_list(self):
        return self._obj_list_prop_

    @property
    def attr_list(self):
        return self._attr_list_prop_

    @property
    def datarange(self):
        return self._data_range_prop_


class VisibleTest(TestCase):
    def test_factory(self):
        obj = VisibleObject('MyHello')
        obj.register()
        obj.register('Hello')
        self.assertEqual(obj, VisibleObject('Hello'))

        o = MyVO._from_class('MyVO', __name__, 'MyTrueVO').register()
        self.assertEqual(o, VisibleObject('MyTrueVO'))

        s = obj.to_json().replace('MyHello', 'NewHello')
        so = VisibleObject.from_json(s).register()
        self.assertEqual(so, VisibleObject('NewHello'))

    def test_link(self):
        obj = MyVO('My')
        first = VisibleObject('FirstProperty')
        obj.modify_object('ObjProp', first)

        second = VisibleObject('FirstProperty')
        self.assertEqual(obj.obj, first)
        self.assertNotEqual(obj.obj, second)

        second.update_link()
        self.assertNotEqual(obj.obj, first)
        self.assertEqual(obj.obj, second)

    def test_persistence(self):
        obj = MyVO('My')
        dic = obj.to_serializable(all_properties=True)
        # test None
        self.assertEqual(dic['NoneProp'], obj.none)
        # test str
        self.assertEqual(dic['StrProp'], obj.str)
        # test int
        self.assertEqual(dic['IntProp'], obj.int)
        # test flt
        self.assertEqual(dic['FltProp'], obj.flt)
        # test FactoryObject
        self.assertEqual(dic['ObjProp'], obj.obj.to_serializable(1))
        # test ObjectList
        self.assertEqual(dic['ObjListProp'], obj.obj_list.to_serializable(1))
        # test AttributeList
        self.assertEqual(dic['AttrListProp'], obj.attr_list.to_serializable(1))
        # test DataRange
        self.assertEqual(dic['DataRangeProp'], obj.datarange.to_serializable(1))
        for k, v in obj.to_serializable().items():
            # print k.ljust(16), str(type(v)).ljust(20), v
            self.assertTrue(isinstance(v, (int, float, str, type(None), list)))
        self.assertTrue(obj.to_json())

    def test_objlist(self):
        names = ['obj' + str(i) for i in range(10)]
        l = ObjectList([MyVO(n) for n in names], object_type=VisibleObject)
        self.assertEqual(l.to_serializable(1), names)
        o = l[0]
        self.assertTrue(o in l)

    def test_attrlist(self):
        names = ['obj' + str(i) for i in range(10)]
        l = [VisibleObject(n) for n in names]
        self.assertTrue(VisibleAttributeList(l))

        l = [object() for n in names]
        self.assertRaises(TypeError, VisibleAttributeList, l)

        l = [MyVO(n).modify_object('DataRangeProp', DataRange()) for n in names]
        self.assertRaises(TypeError, VisibleAttributeList, l)

        # accept Attributes with more than depth 2 -> adding list to value typese
        t = int, float, str, type(None), VisibleObject, list
        a = VisibleAttributeList([o.to_serializable() for o in l], value_types=t)
        for r in a:
            self.assertTrue(isinstance(r, VisibleObject))
        for aa in a:
            aa.register()
        self.assertEqual(a[0], VisibleObject(a[0].to_serializable(1)))

        for r in a.to_serializable():
            for c in r:
                self.assertTrue(dumps(c))  # JSON to_serializable
                self.assertTrue(isinstance(c, (int, float, str, type(None), list)))

        obj = MyVO('My')
        obj.modify_object('ObjListProp', l)
        obj.modify_object('AttrListProp', a)
        self.assertTrue(obj.to_json())

    def test_from_class(self):
        VisibleObject('ME').register()
        o = VisibleObject._from_class('VisibleObject', 'unicum', 'ME')
        self.assertEqual(o, VisibleObject('ME'))

if __name__ == '__main__':
    import sys

    start_time = datetime.now()

    print('')
    print('======================================================================')
    print('')
    print('run %s' % __file__)
    print('in %s' % getcwd())
    print('started  at %s' % str(start_time))
    print('')
    print('----------------------------------------------------------------------')
    print('')

    suite = TestLoader().loadTestsFromModule(__import__("__main__"))
    testrunner = TextTestRunner(stream=sys.stdout, descriptions=2, verbosity=2)
    testrunner.run(suite)

    print('')
    print('======================================================================')
    print('')
    print('ran %s' % __file__)
    print('in %s' % getcwd())
    print('started  at %s' % str(start_time))
    print('finished at %s' % str(datetime.now()))
    print('')
    print('----------------------------------------------------------------------')
    print('')
