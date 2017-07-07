# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)


class DataRange(dict):
    def __init__(self, iterable=None, value_types=(float, int, str, type(None)), none_alias=(None, ' ', '', None),
                 **kwargs):
        self._value_types = value_types
        self._none_alias = none_alias
        self._col_keys = list()
        self._row_keys = list()

        # convert dict into nested list
        if isinstance(iterable, dict):
            iterable = DataRange.__dict_to_nested_list(iterable)

        # replace None alias by None
        none_alias = none_alias if isinstance(none_alias, (tuple, list)) else [none_alias]
        if iterable:
            f = (lambda x: None if x in none_alias else x)
            iterable = [[f(c) for c in r] for r in iterable]

        # slice nested list iterable into (column headers, row headers, data)
        col_keys, row_keys, values = DataRange.__slice_nested_list(iterable)

        # validate iterable (only admissible value types)
        for row_value in values:
            for value in row_value:
                self._validate_value(value)

        # validate column header entries for ambiguity (no int)
        # if any(isinstance(col_key, int) for col_key in col_keys):
        #    raise KeyError('Column keys must not be of type int.')

        # validate row header entries for ambiguity (no int < len(row_headers))
        # if any(isinstance(row_key, int) for row_key in row_keys):
        #    raise KeyError('If row keys are of type int, values not must between 0 and %i.' % len(row_keys))

        if not len(col_keys) == len(set(col_keys)):
            raise KeyError('Col keys must be unique.')
        if not len(row_keys) == len(set(row_keys)):
            raise KeyError('Row keys must be unique.')

        self._col_keys = col_keys
        self._row_keys = row_keys

        iterable = list()
        for row_key, row_values in zip(row_keys, values):
            for col_key, value in zip(col_keys, row_values):
                iterable.append(((row_key, col_key), value))

        super(DataRange, self).__init__(iterable, **kwargs)

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
        if not len(set(col_header)) == len(col_header):
            raise ValueError, 'All column header entries must be unique.'

        # extract row headers if given
        if col_header.count(None):
            i = col_header.index(None)
            col_header.pop(i)
            row_header = [row.pop(i) for row in iterable]
        else:
            row_header = range(len(iterable))
            if not len(set(row_header)) == len(row_header):
                raise ValueError, 'All row header entries must be unique.'

        return col_header, row_header, iterable

    def _validate_value(self, value):
        if not isinstance(value, self._value_types):
            s = ', '.join([str(t) for t in self._value_types])
            t = type(value)
            raise TypeError, \
                'All properties of item in this AttributeList must have type ' \
                'of either one of %s but not %s.' % (s, t)
        return True

    def _validate_key(self, key):
        if not isinstance(key, (list, tuple)) or not len(key) == 2:
            raise KeyError('Key of %s must be (row_key, col_key) tuple.' % self.__class__.__name__)

        r, c = key
        if r not in self._row_keys or c not in self._col_keys:
            s = self.__class__.__name__, str(self._row_keys), str(self._col_keys)
            raise KeyError('Key of %s must be (row_key, col_key) tuple with \n '
                           'row_key in %s \n and col_key in %s' % s)
        return True

    def __repr__(self):
        return self.__class__.__name__ + '(%s)' % str(id(self))

    def __str__(self):
        return self.__class__.__name__ + '(%s)' % str(self.to_serializable())

    def __len__(self):
        return len(self._row_keys)

    def __eq__(self, other):
        assert isinstance(other, DataRange)
        return self.total_list == other.total_list

    def __contains__(self, key):
        try:
            self._validate_key(key)
        except KeyError:
            return False
        return True

    def __copy__(self):
        return self.__class__(self.total_list)

    def __deepcopy__(self, memo):
        return self.__class__(self.to_serializable())

    def __setitem__(self, key, value):
        self._validate_key(key)
        self._validate_value(value)
        super(DataRange, self).__setitem__(key, value)

    def __getitem__(self, key):
        # redirect slice
        if isinstance(key, slice):
            return self.__getslice__(key.start, key.stop)

        # gather which row or col is requested
        # if key in self._row_keys or type(key) is int:
        #     return self.row(key)
        # elif key in self._col_keys:
        #     return self.col(key)

        if not isinstance(key, (list, tuple)) or not len(key) == 2:
            raise KeyError('Key of %s must be row key, col_key or (row key, col key) tuple.' % self.__class__.__name__)

        r, c = key
        # try to pic key if int given
        r = self._row_keys[r] if type(r) is int else r
        c = self._col_keys[c] if type(c) is int else c
        if r not in self._row_keys or c not in self._col_keys:
            s = self.__class__.__name__, str(self._row_keys), str(self._col_keys)
            raise KeyError('Key of %s must be (row_key, col_key) tuple with \n row_key in %s \n and col_key in %s' % s)

        return super(DataRange, self).get((r, c), None)

    def __delitem__(self, key):
        raise NotImplementedError

    def __setslice__(self, i, j, sequence):
        raise NotImplementedError

    def __getslice__(self, i, j):
        if not isinstance(i, (tuple, list)):
            l = len(self._col_keys)
            return self[(i, 0):(j, l)]

        ri, ci = i
        rj, cj = j
        ri = self._row_index(ri)
        rj = self._row_index(rj) + 1 if rj in self._row_keys else rj
        ci = self._col_index(ci)
        cj = self._col_index(cj) + 1 if cj in self._col_keys else cj
        row_keys = self._row_keys[ri:rj]
        col_keys = self._col_keys[ci:cj]
        ret = list()
        for r in row_keys:
            row = [self[r,c] for c in col_keys]
            ret.append(row)
        return ret

    def __delslice__(self, i, j):
        raise NotImplementedError

    def _row_index(self, key):
        return self._row_keys.index(key) if self._row_keys.count(key) else key

    def _col_index(self, key):
        return self._col_keys.index(key) if self._col_keys.count(key) else key

    def row_append(self, key, value):
        """ append new row """
        if key in self._row_keys:
            raise KeyError('Key %s already exists in row keys.' % key)
        if not isinstance(value, (tuple, list)):
            value = [value] * len(self._col_keys)
        if not len(value) == len(self._col_keys):
            raise ValueError('Length of data to set does not meet expected row length of %i' % len(self._col_keys))
        self._row_keys.append(key)
        for c, v in zip(self._col_keys, value):
            self[key, c] = v

    def col_append(self, key, value):
        if key in self._col_keys:
            raise KeyError('Key %s already exists col keys.' % key)
        if not isinstance(value, (tuple, list)):
            value = [value] * len(self._row_keys)
        if not len(value) == len(self._row_keys):
            raise ValueError('Length of data to set does not meet expected col length of %i' % len(self._row_keys))
        self._col_keys.append(key)
        for r, v in zip(self._row_keys, value):
            self[r, key] = v

    def row_keys(self):
        return self._row_keys

    def col_keys(self):
        return self._col_keys

    def row(self, item):
        r = self._row_keys[item] if type(item) == int else item
        return [self.get((r, c)) for c in self._col_keys]

    def col(self, item):
        c = self._col_keys[item] if type(item) == int else item
        return [self.get((r, c)) for r in self._row_keys]

    @property
    def item_list(self):
        return [self.row(r) for r in self.row_keys()]

    @property
    def total_list(self):
        if not self:
            return [[]]
        head = [[None] + self.col_keys()]
        body = [[r] + self.row(r) for r in self.row_keys()]
        return head + body

    def to_serializable(self, level=0):
        ret = list()
        for r in self.total_list:
            l = list()
            for v in r:
                v = v if not hasattr(v, 'to_serializable') else v.to_serializable(level + 1)
                v = self._none_alias[0] if isinstance(v, type(None)) else v
                v = v if isinstance(v, (float, int, type(None))) else str(v)
                l.append(v)
            ret.append(l)
        return ret

    def transpose(self):
        return self.__class__(zip(*self.total_list), value_types=self._value_types, none_alias=self._none_alias)

    def append(self, key, value):
        self.row_append(key, value)

    def extend(self, key, value):
        for k,v in zip(key, value):
            self.row_append(k, v)

    def insert(self, item, key, value=None):
        raise NotImplementedError

    def __reduce__(self):

        return self.__class__, (self.total_list, self._value_types, self._none_alias)

