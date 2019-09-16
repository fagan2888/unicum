# -*- coding: utf-8 -*-

# unicum
# ------
# Python library for simple object cache and factory.
#
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.3, copyright Friday, 13 September 2019
# Website:  https://github.com/sonntagsgesicht/unicum
# License:  Apache License 2.0 (see LICENSE file)


import logging
import sys
import os

from datetime import datetime
from json import dumps, loads, JSONEncoder
from copy import copy, deepcopy
from unittest import TestCase, TestLoader, TextTestRunner
from os import getcwd

sys.path.append('.')
sys.path.append('..')

from unicum import SingletonObject
from unicum import FactoryObject, ObjectList, LinkedObject
from unicum import PersistentObject, PersistentList, PersistentDict, AttributeList, UnicumJSONEncoder
from unicum import VisibleObject, VisibleAttributeList
from unicum import DataRange
from unicum import SessionHandler

_property_order = ["Name", "Class", "Module", "Currency", "Origin", "Notional"]

#logging.basicConfig()


def _silent(func, *args, **kwargs):
    _stout = sys.stdout
    sys.stdout = open(os.devnull, 'w')
    _res = func(*args, **kwargs)
    sys.stdout.close()
    sys.stdout = _stout
    return _res


class _TestDummy(object):
    pass


class SingletonTest(TestCase):
    def setUp(self):
        class SingeltonDummy(_TestDummy, SingletonObject):
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

            def __init__(self, name=None):
                name = self.__class__.__name__ if name is None else name
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

        class FactoryDummy(_TestDummy, Interpolation):
            pass

        self.FactoryDummy = FactoryDummy

        class AnotherFactoryDummy(_TestDummy, Interpolation):
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

        for x, y in zip(list(self.EUR.values()), list(self.USD.values())):
            self.assertTrue(x is y)

        for ek, (k, v), ev in zip(list(self.EUR.keys()), list(self.USD.items()), list(self.Currency.values())):
            self.assertTrue(ek is k)
            self.assertTrue(v is ev)

        self.Currency('EUR').remove()
        self.assertTrue(len(list(self.EUR.items())) is 1)
        self.assertTrue(list(self.EUR.values())[0] is usd)
        self.assertTrue(usd in list(self.Currency.values()))
        self.assertTrue(eur not in list(self.Currency.values()))

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
        self.assertTrue('EUR' in list(self.EUR.keys()))

        names = 'eur', 'Eur', 'EURO', 'euro'
        self.EUR().register(*names)
        keys = list(self.EUR.keys())
        for n in names:
            self.assertTrue(n in keys)

    def test_mixed(self):
        usd = self.USD().register()
        const = self.FactoryDummy().register()

        self.assertTrue(usd in list(self.USD.values()))
        self.assertTrue(usd not in list(self.FactoryDummy.values()))

        self.assertTrue(const not in list(self.USD.values()))
        self.assertTrue(const in list(self.FactoryDummy.values()))

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
        # slices removed with migration to python 3
        # o[0:0] = [eur]
        # self.assertTrue(eur in o)
        # o.pop(0)
        # o[0:0] = ['eur']
        # self.assertTrue(eur in o)

        b = o + ['eur']
        self.assertTrue(isinstance(b, self.CurrencyList))
        self.assertTrue(eur in b)

        b = [eur] + o
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
        d = MyPO().to_serializable(all_properties_flag=True)
        self.assertTrue('Class' in d)
        self.assertTrue(d['MyProperty'] == 'It is mine.')

    def test_dict_to_obj(self):
        e = {'Class': 'PersistentObject'}
        self.assertTrue(type(MyPO.from_serializable(e)) is PersistentObject)
        e = {'Class': 'YourPO', 'Module': __name__}
        self.assertTrue(MyPO.from_serializable(e).to_serializable()['Class'] == 'YourPO')

    def test_modify_obj(self):
        q = MyPO()
        q.modify_object('Property', 'Hello World.')
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

        # slices removed with migration to python 3
        # a[0:0] = [m]
        # self.assertTrue(m in a)
        # a.pop(0)
        # self.assertTrue(m not in a)

        b = a + [m]
        self.assertTrue(isinstance(b, AttributeList))
        self.assertTrue(m in b)

        b = [m] + a
        self.assertTrue(not isinstance(b, AttributeList))
        self.assertTrue(m in b)

    def test_persistentlist(self):
        l = PersistentList(list(range(10)))
        l.append(MyPO())
        s = l.to_serializable()
        self.assertNotEqual(l, s)
        for i, j in zip(l, s):
            if hasattr(i, 'to_serializable'):
                i = i.to_serializable(1)
            self.assertEqual(i, j)
            # todo: add tests interacting with PersistenObject

    def test_persistentdict(self):
        l = PersistentDict({'A': 1, 'B': MyPO(), 'C': 'ABC'})
        s = l.to_serializable()
        self.assertNotEqual(l, s)
        for i, j in zip(l, s):
            if hasattr(i, 'to_serializable'):
                i = i.to_serializable(1)
            self.assertEqual(i, j)
            # todo: add tests interacting with PersistenObject


class DataRangeTest(TestCase):
    def setUp(self):
        h = '', 'A', 'B', 'C', 'D'
        x = 'X', 1, 2, 3, 4
        y = 'Y', 4, 5, 6, 7
        z = 'Z', 7, 8, 9, 10
        self.datarange = DataRange([h, x, y, z])
        pass

    def test_init(self):
        new_datarange = DataRange(self.datarange.to_serializable())
        self.assertEqual(self.datarange.to_serializable(), new_datarange.to_serializable())

        new_datarange = DataRange(self.datarange)
        self.assertEqual(self.datarange.to_serializable(), new_datarange.to_serializable())

    def test_keys(self):
        self.assertEqual(self.datarange.col_keys(), ['A', 'B', 'C', 'D'])
        self.assertEqual(self.datarange.row_keys(), ['X', 'Y', 'Z'])

    def test_get(self):
        self.assertEqual(self.datarange.get(('X', 'A')), 1)
        self.assertEqual(self.datarange.row('X'), [1, 2, 3, 4])
        self.assertEqual(self.datarange.col('D'), [4, 7, 10])
        # self.assertEqual(self.datarange[0][-1], 4)
        # self.assertEqual(self.datarange[0, -1], 4)
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
        self.assertTrue('U' not in self.datarange.row_keys())
        self.datarange['U', 'C'] = 4
        self.assertTrue('U' in self.datarange.row_keys())

    def test_append(self):
        self.datarange.append('W', list(range(4)))
        l = lambda: self.datarange.row_append('W', list(range(4)))
        self.assertRaises(KeyError, l)
        self.assertEqual(len(self.datarange), 4)
        self.assertEqual(self.datarange.row_keys()[-1], 'W')
        self.assertEqual(self.datarange.row('W'), list(range(4)))

        self.datarange.row_append('U', list(range(2, 6)))
        self.assertEqual(self.datarange.row('U'), list(range(2, 6)))

        self.datarange.col_append('T', list(range(5)))
        self.assertEqual(self.datarange.col('T'), list(range(5)))

    def test_copy(self):
        self.assertEqual(self.datarange, copy(self.datarange))
        self.assertEqual(type(self.datarange), type(copy(self.datarange)))
        self.assertEqual(self.datarange, deepcopy(self.datarange))
        self.assertEqual(type(self.datarange), type(deepcopy(self.datarange)))

    def test_transpose(self):
        # self.assertEqual(type(list(self.datarange)), list)
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

    def test_json(self):
        for i in [None, 0, 1, 2]:
            unicum_json = dumps(self.datarange, cls=UnicumJSONEncoder, indent=i)
            standard_json = dumps(self.datarange.to_serializable(), indent=i)
            unicum_json_2 = dumps(DataRange(loads(standard_json)), cls=UnicumJSONEncoder, indent=i)
            standard_json_2 = dumps(DataRange(loads(unicum_json)).to_serializable(), indent=i)
            self.assertEqual(unicum_json_2, unicum_json_2)
            self.assertEqual(standard_json, standard_json_2)


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
        dic = obj.to_serializable(all_properties_flag=True)
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
        for k, v in list(obj.to_serializable().items()):
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

    def test_json(self):
        objs = [1, 2, 3], [1e-1, 1e-1, 1e1, 1e3], 0.12345, 99, 'abc', None, int(12345), {'A':3, 3:4, 'a':'B'}
        for i in [None, 0, 1, 2]:
            for o in objs:
                self.assertEqual(UnicumJSONEncoder(indent=i).encode(o), JSONEncoder(indent=i).encode(o))
                self.assertEqual(UnicumJSONEncoder(indent=i).encode(o), JSONEncoder(indent=i).encode(o))

        rng = DataRange([[' ', 'X'], [1, 2], [0, 1e10]])
        obj = MyVO().modify_object('DataRangeProp', rng)
        unicum_json = dumps(obj, cls=UnicumJSONEncoder, indent=2, key_order=("Module", "Name", "Class",))
        self.assertTrue(unicum_json.find("Module") < unicum_json.find("Name"))
        self.assertTrue(unicum_json.find("Name") < unicum_json.find("Class"))
        self.assertEqual(len(unicum_json.split("\n")), 2+len(obj.to_serializable())+len(rng)+2)

        for i in [None, 0, 1, 2]:
            unicum_json = dumps(obj, cls=UnicumJSONEncoder, indent=i)
            standard_json = dumps(obj.to_serializable(), indent=i)
            unicum_json_2 = dumps(MyVO.from_json(standard_json), cls=UnicumJSONEncoder, indent=i)
            standard_json_2 = dumps(MyVO.from_json(unicum_json).to_serializable(), indent=i)
            self.assertEqual(unicum_json_2, unicum_json_2)
            self.assertEqual(standard_json, standard_json_2)

    def test_json_1(self):
        e = {'Class': 'VisibleObject', 'Module': 'unicum.visibleobject'}
        j = dumps(e)
        o = VisibleObject.from_json(j)
        self.assertEqual(type(o), VisibleObject)

        e = {'Name': 'my vo', 'Class': 'MyVO', 'Module': __name__, 'StrProp': 'It is mine.'}
        j = dumps(e, indent=2, sort_keys=True)
        o = VisibleObject.from_json(j)
        self.assertTrue(type(o) is MyVO)
        oj = o.to_json(indent=2, property_order=sorted(e.keys()))
        self.assertEqual(oj, j)
        self.assertEqual(o.to_serializable(), VisibleObject.from_serializable(e).to_serializable())


class TestVisibleObject(VisibleObject):

    def __init__(self, *args, **kwargs):
        super(TestVisibleObject, self).__init__(*args, **kwargs)
        self._folder_ = ''
        self._float_ = 0.


class SessionTest(TestCase):

    def test_session(self):
        my_session_id = 'my session'
        my_object_name = 'my object'
        handler = SessionHandler('unittests', 'TestVisibleObject')
        self.assertFalse(handler.validate_session(my_session_id))
        session_id = handler.start_session(my_session_id)
        self.assertEqual(session_id, my_session_id)
        self.assertTrue(handler.validate_session(session_id))
        self.assertTrue(handler.call_session(session_id, 'create', {'name': my_object_name, 'register_flag': True} ))

        rng = handler.call_session(session_id, 'to_range', {'self': my_object_name, 'all_properties_flag': True})
        self.assertEqual('Name', rng[0][0])
        self.assertEqual(my_object_name, rng[0][1])
        self.assertEqual('Class', rng[1][0])
        self.assertEqual('TestVisibleObject', rng[1][1])

        json = handler.call_session(session_id, 'to_json', {'self': my_object_name, 'all_properties_flag': True})
        self.assertTrue(isinstance(json, str))
        d = loads(json)
        self.assertEqual(d['Name'], my_object_name)
        self.assertEqual(d['Class'], 'TestVisibleObject')

        self.assertTrue(handler.validate_session(session_id))
        handler.stop_session(session_id)


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
    print(('ran %s' % __file__))
    print(('in %s' % getcwd()))
    print(('started  at %s' % str(start_time)))
    print(('finished at %s' % str(datetime.now())))
    print('')
    print('----------------------------------------------------------------------')
    print('')
