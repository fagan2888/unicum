# -*- coding: utf-8 -*-

# unicum
# ------
# Python library for simple object cache and factory.
# 
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.3, copyright Wednesday, 18 September 2019
# Website:  https://github.com/sonntagsgesicht/unicum
# License:  Apache License 2.0 (see LICENSE file)


from json import JSONEncoder
from json.encoder import encode_basestring_ascii, encode_basestring, INFINITY

from .datarange import DataRange
from .persistentobject import AttributeList
from .factoryobject import ObjectList

FLOAT_REPR = float.__repr__


class UnicumJSONEncoder(JSONEncoder):
    def __init__(self, key_order=list(), all_properties_flag=False, *args, **kwargs):
        self._order = key_order
        self._all_properties = all_properties_flag
        super(UnicumJSONEncoder, self).__init__(*args, **kwargs)

    def default(self, obj, level=0):
        if hasattr(obj, 'to_serializable'):
            return obj.to_serializable(all_properties_flag=self._all_properties, recursive=False, level=level)
        else:
            return super(UnicumJSONEncoder, self).default(obj)

    def iterencode(self, o, _one_shot=False):
        """Encode the given object and yield each string
        representation as available.

        For example::

            for chunk in JSONEncoder().iterencode(bigobject):
                mysocket.write(chunk)

        """
        if self.check_circular:
            markers = {}
        else:
            markers = None
        if self.ensure_ascii:
            _encoder = encode_basestring_ascii
        else:
            _encoder = encode_basestring
        # turned off sc
        # #if self.encoding != 'utf-8':
        #    def _encoder(o, _orig_encoder=_encoder, _encoding=self.encoding):
        #        if isinstance(o, str):
        #            o = o.decode(_encoding)
        #       return _orig_encoder(o)

        def floatstr(o, allow_nan=self.allow_nan,
                     _repr=FLOAT_REPR, _inf=INFINITY, _neginf=-INFINITY):
            # Check for specials.  Note that this type of test is processor
            # and/or platform-specific, so do tests which don't depend on the
            # internals.

            if o != o:
                text = 'NaN'
            elif o == _inf:
                text = 'Infinity'
            elif o == _neginf:
                text = '-Infinity'
            else:
                return _repr(o)

            if not allow_nan:
                raise ValueError(
                    "Out of range float values are not JSON compliant: " +
                    repr(o))

            return text

        _iterencode = _make_iterencode(
            markers, self.default, _encoder, self.indent, floatstr,
            self.key_separator, self.item_separator, self.sort_keys,
            self.skipkeys, _one_shot, self._order)

        return _iterencode(o, 0)


def _make_iterencode(markers, _default, _encoder, _indent, _floatstr,
                     _key_separator, _item_separator, _sort_keys, _skipkeys, _one_shot, _key_order,
                     ## HACK: hand-optimized bytecode; turn globals into locals
                     ValueError=ValueError,
                     dict=dict,
                     float=float,
                     id=id,
                     int=int,
                     isinstance=isinstance,
                     list=list,
                     str=str,
                     long=int,
                     tuple=tuple,
                     ):
    def _iterencode_list(lst, _current_indent_level, level=0):
        if not lst:
            yield '[]'
            return
        if markers is not None:
            markerid = id(lst)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = lst
        buf = '['
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + (' ' * (_indent * _current_indent_level))
            separator = _item_separator + newline_indent
            buf += newline_indent
        else:
            newline_indent = None
            separator = _item_separator
        first = True
        for value in lst:
            if first:
                first = False
            else:
                buf = separator
            if isinstance(value, str):
                yield buf + _encoder(value)
            elif value is None:
                yield buf + 'null'
            elif value is True:
                yield buf + 'true'
            elif value is False:
                yield buf + 'false'
            elif isinstance(value, int):
                yield buf + str(value)
            elif isinstance(value, float):
                yield buf + _floatstr(value)
            else:
                yield buf
                if isinstance(value, (DataRange, AttributeList)):
                    chunks = _iterencode_data_range(value.to_serializable(_current_indent_level), _current_indent_level)
                elif isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level, level=level)
                for chunk in chunks:
                    yield chunk
        if newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + (' ' * (_indent * _current_indent_level))
        yield ']'
        if markers is not None:
            del markers[markerid]

    def _iterencode_dict(dct, _current_indent_level, level=0):
        if not dct:
            yield '{}'
            return
        if isinstance(dct, (DataRange, AttributeList)):
            _iterencode_data_range(dct, _current_indent_level)
        if markers is not None:
            markerid = id(dct)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = dct
        yield '{'
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + (' ' * (_indent * _current_indent_level))
            item_separator = _item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            item_separator = _item_separator
        first = True
        if _sort_keys:
            items = sorted(list(dct.items()), key=lambda kv: kv[0])
        else:
            items = iter(dct.items())
        if _key_order:
            old_items = list(items)
            new_items = list()
            for ko in _key_order:
                for k, v in old_items:
                    if k.upper() == ko.upper():
                        new_items.append((k, v))
            for k, v in old_items:
                if (k,v) not in new_items:
                    new_items.append((k, v))
            items = new_items
        for key, value in items:
            if isinstance(key, str):
                pass
            # JavaScript is weakly typed for these, so it makes sense to
            # also allow them.  Many encoders seem to do something like this.
            elif isinstance(key, float):
                key = _floatstr(key)
            elif key is True:
                key = 'true'
            elif key is False:
                key = 'false'
            elif key is None:
                key = 'null'
            elif isinstance(key, int):
                key = str(key)
            elif _skipkeys:
                continue
            else:
                raise TypeError("key " + repr(key) + " is not a string")
            if first:
                first = False
            else:
                yield item_separator
            yield _encoder(key)
            yield _key_separator
            if isinstance(value, str):
                yield _encoder(value)
            elif value is None:
                yield 'null'
            elif value is True:
                yield 'true'
            elif value is False:
                yield 'false'
            elif isinstance(value, int):
                yield str(value)
            elif isinstance(value, float):
                yield _floatstr(value)
            else:
                if isinstance(value, (DataRange, AttributeList)):
                    chunks = _iterencode_data_range(value.to_serializable(_current_indent_level), _current_indent_level)
                elif isinstance(value, ObjectList):
                    chunks = _iterencode_list(value, _current_indent_level, level=1)
                elif isinstance(value, (list, tuple)):
                    chunks = _iterencode_list(value, _current_indent_level)
                elif isinstance(value, dict):
                    chunks = _iterencode_dict(value, _current_indent_level)
                else:
                    chunks = _iterencode(value, _current_indent_level, level=1)
                for chunk in chunks:
                    yield chunk
        if newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + (' ' * (_indent * _current_indent_level))
        yield '}'
        if markers is not None:
            del markers[markerid]

    def _iterencode_data_range(rng, _current_indent_level):
        if not rng:
            yield '[[]]'
            return
        if markers is not None:
            markerid = id(rng)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = rng
        buf = '['
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = '\n' + (' ' * (_indent * _current_indent_level))
            separator = _item_separator + newline_indent
            buf += newline_indent
        else:
            newline_indent = None
            separator = _item_separator
        first = True
        # simple gathering of cell space
        # cell_space = max(max(map(len, _iterencode_data_range_line(item, 0, 0))) for item in rng)
        # col specific gathering of cell space
        cell_space = list(max(list(map(len, _iterencode_data_range_line(item, 0, 0)))) for item in zip(*rng))
        for value in rng:
            if first:
                first = False
            else:
                buf = separator
            yield buf
            chunks = _iterencode_data_range_line(value, _current_indent_level, cell_space)
            for chunk in chunks:
                yield chunk
        if newline_indent is not None:
            _current_indent_level -= 1
            yield '\n' + (' ' * (_indent * _current_indent_level))
        yield ']'
        if markers is not None:
            del markers[markerid]

    def _iterencode_data_range_line(rng, _current_indent_level, cell_len=12):
        if not isinstance(cell_len, (tuple, list)):
            cell = [cell_len] * len(rng)
        else:
            if not len(cell_len) == len(rng):
                raise RuntimeError("Error parsing data range line.")
            cell = cell_len
        if markers is not None:
            markerid = id(rng)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = rng
        buf = '['
        if _indent is not None:
            _current_indent_level += 1
            newline_indent = ''
            separator = _item_separator
            buf += ' ' + newline_indent
        else:
            newline_indent = None
            separator = _item_separator
        first = True
        for value, space in zip(rng, cell):
            if first:
                first = False
            else:
                buf = separator
            yield buf
            chunks = _iterencode(value, _current_indent_level, level=1)
            for chunk in chunks:
                if newline_indent is not None and space:
                    chunk = chunk.rjust(space) + ' '
                yield chunk
        if newline_indent is not None:
            _current_indent_level -= 1
        yield ']'
        if markers is not None:
            del markers[markerid]

    def _iterencode(o, _current_indent_level, level=0):
        if isinstance(o, str):
            yield _encoder(o)
        elif o is None:
            yield 'null'
        elif o is True:
            yield 'true'
        elif o is False:
            yield 'false'
        elif isinstance(o, int):
            yield str(o)
        elif isinstance(o, float):
            yield _floatstr(o)
        elif isinstance(o, (DataRange, AttributeList)):
            for chunk in _iterencode_data_range(o.to_serializable(_current_indent_level), _current_indent_level):
                yield chunk
        elif isinstance(o, ObjectList):
            for chunk in _iterencode_list(o, _current_indent_level, level=1):
                yield chunk
        elif isinstance(o, (list, tuple)):
            for chunk in _iterencode_list(o, _current_indent_level):
                yield chunk
        elif isinstance(o, dict):
            for chunk in _iterencode_dict(o, _current_indent_level):
                yield chunk
        else:
            if markers is not None:
                markerid = id(o)
                if markerid in markers:
                    raise ValueError("Circular reference detected")
                markers[markerid] = o
            o = _default(o, level=level)
            for chunk in _iterencode(o, _current_indent_level, level=1):
                yield chunk
            if markers is not None:
                del markers[markerid]

    return _iterencode
