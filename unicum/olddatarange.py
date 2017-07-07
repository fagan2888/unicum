# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)


class IndexedList(list):
    def __init__(self, keys=list(), values=None):
        # fixme imput no or empty list (just headers)
        values = keys if values is None else values
        keys = [str(v) for v in values] if keys is values else keys

        if isinstance(values, IndexedList):
            keys = values.keys()
            values = values.values()
        if len(values) is not len(keys):
            raise IndexError, '%s requires exactly one key for each item' % self.__class__.__name__
        if len(set(keys)) is not len(keys):
            raise ValueError, 'In %s keys must be unique' % self.__class__.__name__
        self._keys = dict(zip(keys, range(len(values))))
        super(IndexedList, self).__init__(values)

    def __add__(self, other):
        assert isinstance(other, IndexedList)
        keys = self.keys() + other.keys()
        values = self.values() + other.values()
        return self.__class__(values, keys)

    def __iadd__(self, other):
        assert isinstance(other, IndexedList)
        keys = self.keys() + other.keys()
        values = self.values() + other.values()
        return self.__class__(values, keys)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            s = key.start if key.start else 0
            e = key.stop if key.stop else len(self)
            self.__setslice__(s, e, value)
        else:
            index = self._keys[key] if key in self._keys else key
            super(IndexedList, self).__setitem__(index, value)

    def __getitem__(self, item):
        if isinstance(item, slice):
            s = item.start if item.start else 0
            e = item.stop if item.stop else len(self)
            return self.__getslice__(s, e)
        else:
            index = self._keys[item] if item in self._keys else item
            return super(IndexedList, self).__getitem__(index)

    def __delitem__(self, key):
        if isinstance(key, slice):
            s = key.start if key.start else 0
            e = key.stop if key.stop else len(self)
            self.__delslice__(s, e)
        else:
            index = self._keys[key] if key in self._keys else key
            super(IndexedList, self).__delitem__(index)

    def __setslice__(self, i, j, sequence):
        i_index = self._keys[i] if i in self._keys else i
        j_index = self._keys[j] + 1 if j in self._keys else j
        super(IndexedList, self).__setslice__(i_index, j_index, sequence)

    def __getslice__(self, i, j):
        i_index = self._keys[i] if i in self._keys else i
        i_index = len(self) if i is None else i_index
        j_index = self._keys[j] + 1 if j in self._keys else j
        j_index = len(self) if j is None else j_index
        return super(IndexedList, self).__getslice__(i_index, j_index)

    def __delslice__(self, i, j):
        i_index = self._keys[i] if i in self._keys else i
        j_index = self._keys[j] + 1 if j in self._keys else j
        super(IndexedList, self).__delslice__(i_index, j_index)

    def insert(self, item, key, value=None):
        index = self._keys[item] if item in self._keys else item
        value = key if value is None else value
        key = str(value) if key is value else key

        # validate key
        if key in self._keys:
            raise KeyError, 'Key %s already given.' % str(item)
        super(IndexedList, self).insert(index, value)
        # rebuild _keys
        keys = self.keys()
        keys.insert(index, key)
        self._keys = dict(zip(keys, range(len(self))))

    def append(self, key, value=None):
        value = key if value is None else value
        key = str(value) if key is value else key
        # validate key
        if key in self._keys:
            raise KeyError, 'Key %s already given.' % str(key)
        self._keys[key] = len(self)
        super(IndexedList, self).append(value)

    def extend(self, keys, values=None):
        values = keys if values is None else values
        keys = [str(v) for v in values] if keys is values else keys

        if isinstance(values, IndexedList):
            keys = values.keys()
            values = values.values()

        for k in keys:
            if k in self._keys:
                raise KeyError, 'Key %s already given.' % str(k)
            self._keys[k] = len(self._keys)
        super(IndexedList, self).extend(values)

    def keys(self):
        l = (lambda x, y: self._keys[x] - self._keys[y])
        return sorted(self._keys.keys(), l)

    def values(self):
        return [self[k] for k in self.keys()]

    def items(self):
        return [(k, self[k]) for k in self.keys()]


class DataRange(IndexedList):
    """ DataRange class """

    def __init__(self, iterable=None, value_types=(float, int, str, type(None)), none_alias=(None, ' ', '', None)):
        self._value_types = value_types
        self._none_alias = none_alias

        # covert dict into nested list
        if isinstance(iterable, dict):
            iterable = DataRange.__dict_to_nested_list(iterable)

        # replace None alias by None
        none_alias = none_alias if isinstance(none_alias, (tuple, list)) else [none_alias]
        if iterable:
            f = (lambda x: None if x in none_alias else x)
            iterable = [[f(c) for c in r] for r in iterable]

        # slice nested list iterable into (column headers, row headers, data)
        ch, rh, values = DataRange.__slice_nested_list(iterable)
        # todo validate column header entries for ambiguity (no int < len(col_headers))
        # todo validate row header entries for ambiguity (no int < len(row_headers))
        # todo validate iterable (only admissible value types)

        super(DataRange, self).__init__(rh, [IndexedList(ch, v) for v in values])

    @staticmethod
    def __dict_to_nested_list(iterable):
        item_list = [iterable.keys()]
        for i in xrange(max(map(len, iterable.values()))):
            item_list.append([iterable[k][i] for k in item_list[0]])
        return item_list

    @staticmethod
    def __slice_nested_list(iterable):
        if not iterable:
            return list(), list(), list()

        # extract column headers from first row
        col_header = iterable.pop(0)
        if len(set(col_header)) is not len(col_header):
            raise ValueError, 'All column header entries must be unique.'

        # extract row headers if given
        if col_header.count(None):
            i = col_header.index(None)
            col_header.pop(i)
            row_header = [row.pop(i) for row in iterable]
        else:
            row_header = range(len(iterable))
        if len(set(row_header)) is not len(row_header):
            raise ValueError, 'All row header entries must be unique.'

        return col_header, row_header, iterable

    def __repr__(self):
        return self.__class__.__name__ + '(%s)' % str(id(self))

    def __str__(self):
        return self.__class__.__name__ + '(%s)' % str(self.to_serializable())

    def __iter__(self):
        return super(DataRange, self).__iter__()

    def __setitem__(self, key, value):
        # todo validate value (only admissible value types)

        if isinstance(key, slice):
            return self.__setslice__(key.start, key.stop)

        if key in self.row_keys() or type(key) is int:
            return super(DataRange, self).__setitem__(key, value)

        if len(key) == 2:
            r, c = key
            return super(DataRange, self).__getitem__(r).__setitem__(c, value)

        raise KeyError, 'Key %s not found.' % repr(key)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__getslice__(item.start, item.stop)

        if item in self.row_keys() or type(item) is int:
            return super(DataRange, self).__getitem__(item)

        if len(item) == 2:
            r, c = item
            return super(DataRange, self).__getitem__(r).__getitem__(c)

        raise KeyError, 'Key %s not found.' % repr(item)

    def __delitem__(self, key):
        raise NotImplementedError

    def __setslice__(self, i, j, sequence):
        raise NotImplementedError

    def __getslice__(self, i, j):
        if isinstance(i, (tuple, list)):
            row_start, col_start = i
            row_stop, col_stop = j
            row_start = row_start if row_start else 0
            row_stop = row_stop if row_stop is not None else len(self.row_keys())
            col_start = col_start if col_start else 0
            col_stop = col_stop if col_stop is not None else len(self.col_keys())
            return_list = [d.__getslice__(col_start, col_stop) for d in
                           super(DataRange, self).__getslice__(row_start, row_stop)]
        else:
            i = 0 if i is None else i
            j = len(self.row_keys()) if j is None else j
            return_list = super(DataRange, self).__getslice__(i, j)
        # return self.__class__(return_list, value_types=self._value_types, none_alias=self._none_alias)
        return return_list

    def __delslice__(self, i, j):
        raise NotImplementedError

    def insert(self, item, key, value=None):
        raise NotImplementedError

    def pop(self, index=None):
        raise NotImplementedError

    def append(self, key, value=None):
        if value is None:
            value = [None] * len(self.col_keys())
        if not isinstance(value, list) and not len(value) == len(self.col_keys()):
            raise ValueError
        if isinstance(value, IndexedList):
            if not value.keys() == self.col_keys():
                raise KeyError
        else:
            value = IndexedList(self.col_keys(), value)
        super(DataRange, self).append(key, value)

    def extend(self, keys, values=None):
        raise NotImplementedError

    def transpose(self):
        return self.__class__(zip(*self._total), value_types=self._value_types, none_alias=self._none_alias)

    def row_keys(self):
        return list(super(DataRange, self).keys())

    def col_keys(self):
        return list(super(DataRange, self).__getitem__(0).keys())

    def keys(self):
        keys = list()
        for row_key in self.row_keys():
            for col_key in self.col_keys():
                keys.append((row_key, col_key))
        return keys

    def values(self):
        return [self[k] for k in self.keys()]

    def items(self):
        return [(k, self[k]) for k in self.keys()]

    @property
    def _total(self):
        if not self:
            return [[]]
        ret = [[None] + self.col_keys()]
        for r in self.row_keys():
            l = [r]
            for v in self[r]:
                l.append(v)
            ret.append(l)
        return ret

    def to_serializable(self, level=0):
        ret = list()
        for r in self._total:
            l = list()
            for v in r:
                v = v if not hasattr(v, 'to_serializable') else v.to_serializable(level + 1)
                v = self._none_alias[0] if isinstance(v, type(None)) else v
                v = v if isinstance(v, (float, int, type(None))) else str(v)
                l.append(v)
            ret.append(l)
        return ret

    def row(self, item):
        return self[item]

    def col(self, item):
        return [self[r][item] for r in self.row_keys()]
