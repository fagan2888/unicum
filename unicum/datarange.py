# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)

LEFT_TOP = None


class DataRange(object):
    def __init__(self, iterable=None, value_types=(float, int, str, type(None)), none_alias=(None, ' ', '', 'None'),
                 **kwargs):
        self._value_types = value_types
        self._none_alias = none_alias
        self._col_keys = list()
        self._row_keys = list()

        # convert dict into nested list
        if isinstance(iterable, dict):
            iterable = DataRange.__dict_to_nested_list(iterable)

        # convert DataRange into nested list
        if isinstance(iterable, DataRange):
            iterable = iterable.to_serializable()

        # replace None alias by None
        none_alias = none_alias if isinstance(none_alias, (tuple, list)) else [none_alias]
        if iterable:
            f = (lambda x: None if x in none_alias else x)
            iterable = [[f(c) for c in r] for r in iterable]

        # slice nested list iterable into (column headers, row headers, data)
        col_keys, row_keys, item_list = DataRange.__slice_nested_list(iterable)

        # validate iterable (only admissible value types)
        for row_value in item_list:
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
        self._item_list = item_list

        iterable = list()
        for row_key, row_values in zip(row_keys, item_list):
            for col_key, value in zip(col_keys, row_values):
                iterable.append(((row_key, col_key), value))

        # super(DataRange, self).__init__(iterable, **kwargs)
        self._dict = dict(iterable, **kwargs)
        self._hash = hash(self)

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

            msg = 'All properties of item in this DataRange must have type ' \
                  'of either one of %s but not %s.' % (s, t)
            raise TypeError(msg)

        return True

    def _validate_key_format(self, key):
        if not isinstance(key, (list, tuple)) or not len(key) == 2:
            s = self.__class__.__name__, key.__class__.__name__
            raise KeyError('Key of %s must be (row_key, col_key) tuple not %s.' % s)

    def _validate_key_existence(self, key):
        self._validate_key_format(key)
        r, c = key
        if r not in self._row_keys or c not in self._col_keys:
            s = self.__class__.__name__, str(self._row_keys), str(self._col_keys)
            msg = 'Key of %s must be (row_key, col_key) tuple with \n row_key in %s \n and col_key in %s' % s
            raise KeyError(msg)
        return True

    def __hash__(self):
        return hash(frozenset(self._dict.items()))

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
            self._validate_key_existence(key)
        except KeyError:
            return False
        return True

    def __copy__(self):
        return self.__class__(self.total_list)

    def __deepcopy__(self, memo):
        return self.__class__(self.to_serializable())

    def __setitem__(self, key, value):
        self._validate_key_format(key)
        if not key[0] in self.row_keys():
            self._row_keys.append(key[0])
        if not key[1] in self.col_keys():
            self._col_keys.append(key[1])
        self._validate_value(value)
        # super(DataRange, self).__setitem__(key, value)
        self._dict[key] = value

    def __getitem__(self, key):
        # redirect slice
        if isinstance(key, slice):
            return self.__getslice__(key.start, key.stop)

        # gather which row or col is requested
        # if key in self._row_keys or type(key) is int:
        #     return self.row(key)
        # elif key in self._col_keys:
        #     return self.col(key)

        self._validate_key_format(key)

        r, c = key
        self._validate_key_existence((r, c))

        # return super(DataRange, self).get((r, c), None)
        return self._dict.get(key, None)

    def __delitem__(self, key):
        raise NotImplementedError

    def __setslice__(self, i, j, sequence):
        raise NotImplementedError

    def __getslice__(self, i, j):
        self._update_cache()
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
            row = [self[r, c] for c in col_keys]
            ret.append(row)
        return ret

    def __delslice__(self, i, j):
        raise NotImplementedError

    def update(self, other):
        return self._dict.update(other)

    def keys(self):
        return self._dict.keys()

    def values(self):
        return self._dict.values()

    def items(self):
        return self._dict.items()

    def get(self, key, default=None):
        return self._dict.get(key, default)

    def pop(self, key, default=None):
        return self._dict.pop(key, default)

    def popitem(self):
        return self._dict.popitem()

    def _row_index(self, key):
        return self._row_keys.index(key) if self._row_keys.count(key) else key

    def _col_index(self, key):
        return self._col_keys.index(key) if self._col_keys.count(key) else key

    def row_append(self, row_key, value_list):
        """
        append a new row to a DataRange

        :param row_key: a string
        :param value_list: a list
        """
        if row_key in self._row_keys:
            raise KeyError('Key %s already exists in row keys.' % row_key)
        if not len(value_list) == len(self._col_keys):
            raise ValueError('Length of data to set does not meet expected row length of %i' % len(self._col_keys))
        self._row_keys.append(row_key)
        for c, v in zip(self._col_keys, value_list):
            self[row_key, c] = v

    def col_append(self, col_key, value_list):
        """
        append a new row to a DataRange

        :param row_key: a string
        :param value_list: a list
        """
        if col_key in self._col_keys:
            raise KeyError('Key %s already exists col keys.' % col_key)
        if not isinstance(value_list, (tuple, list)):
            value_list = [value_list] * len(self._row_keys)
        if not len(value_list) == len(self._row_keys):
            raise ValueError('Length of data to set does not meet expected col length of %i' % len(self._row_keys))
        self._col_keys.append(col_key)
        for r, v in zip(self._row_keys, value_list):
            self[r, col_key] = v

    def _update_cache(self):
        if not self._hash == hash(self):
            row_keys = sorted(list(set([row_key for row_key, col_key in self.keys()
                                        if row_key not in self._row_keys])))
            self._row_keys += row_keys

            col_keys = sorted(list(set([col_key for row_key, col_key in self.keys()
                                        if col_key not in self._col_keys])))
            self._col_keys += col_keys

            self._item_list = [[self.get((r, c)) for c in self._col_keys] for r in self._row_keys]
            self._hash = hash(self)

    # @property
    def row_keys(self):
        self._update_cache()
        return self._row_keys

    # @property
    def col_keys(self):
        self._update_cache()
        return self._col_keys

    def row(self, item):
        i = self.row_keys().index(item)
        return self.item_list[i]

    def col(self, item):
        j = self.col_keys().index(item)
        return [row[j] for row in self.item_list]

    @property
    def item_list(self):
        self._update_cache()
        return self._item_list

    @property
    def total_list(self):
        if not self:
            return [[]]
        total = [[LEFT_TOP] + self.col_keys()]
        for r, row in zip(self.row_keys(), self.item_list):
            total.append([r] + row)
        return total

    def to_serializable(self, level=0, all_properties_flag=False, recursive=True):
        ret = list()
        for r in self.total_list:
            l = list()
            for v in r:
                if recursive:
                    v = v if not hasattr(v, 'to_serializable') else v.to_serializable(level + 1, all_properties_flag)
                    v = v if isinstance(v, (float, int, type(None))) else str(v)
                v = self._none_alias[0] if isinstance(v, type(None)) else v
                l.append(v)
            ret.append(l)
        return ret

    def transpose(self):
        return self.__class__(zip(*self.total_list), value_types=self._value_types, none_alias=self._none_alias)

    def append(self, key, value):
        self.row_append(key, value)

    def extend(self, other):
        assert isinstance(other, self.__class__)
        for key, value in other.items():
            assert key not in self
            self[key] = value

        return self

    def insert(self, item, key, value=None):
        raise NotImplementedError

    def __reduce__(self):

        return self.__class__, (self.total_list, self._value_types, self._none_alias)
