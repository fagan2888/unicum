"""
This module contains the JSON Writer class.
"""

class JSONWriter(object):
    """
    A writer to write json formated strings.
    This class provides method to wite list, dicts and property values in json format.
    """
    def __init__(self, indent="\t"):
        """
        Initializes the JSONWriter.
        """
        self._default_prefix = ' ' * indent if type(indent) is int else indent


    def write_obj(self, properties, property_order, table_names, tables):
        """
        Writes an object, which consists of properties and tables in a json formated string.
        """
        lines = self.get_dict_in_json_list(properties, property_order)
        for i in xrange(len(table_names)):
            tab = self.write_table(tables[i])
            lines.append(self.write_property_value(table_names[i], tab, value_in_quotes=False))
        return self.write_obj_from_lines(lines)

    def get_dict_in_json_list(self, properties, property_order=[]):
        """
        Writes a dictionary into a list of json strings, where the given property
        order will be considered.
        Returns a list of strings.
        """
        json_props = []
        for prop in property_order:
            if prop in properties:
                json_props.append(self.write_property_value(prop, properties[prop]))
        for prop in properties.keys():
            if not prop in property_order:
                json_props.append(self.write_property_value(prop, properties[prop]))
        return json_props

    def write_property_value(self, prop, value, prefix_sign=None, value_in_quotes=True):
        """
        Writes the given property value pair in json formated string.
        It is checked, if the value is a float value, which is displayd without quote signs,
        otherwise is rounded with quotes,
        except the optional argument 'value_in_quotes' is set to false.
        """
        pre = prefix_sign if prefix_sign is not None else self._default_prefix
        val = self._in_quotes_if_necessary(value) if value_in_quotes else value
        return pre + self._in_quotes_if_necessary(prop) + ": " + val

    def write_table(self, table):
        """
        Writes a table (object which has col_keys, row_keys and
        a corresponding value(row_key, col_key) method)
        in a data range json, where each column is displayed in one line.
        Returns the json string.
        """
        rows = []
        header = [self._in_quotes_if_necessary(e) for e in table.col_keys]
        header.insert(0, '" "')
        rows.append("\t" + self.write_array_row(header))
        for row_key in sorted(table.row_keys):
            row = [self._in_quotes_if_necessary(table.value(row_key, c)) for c in table.col_keys]
            row.insert(0, self._in_quotes_if_necessary(row_key))
            rows.append(self.write_array_row(row))
        ret = self.write_obj_from_lines(rows, "[", "\t\t]", ",\n\t")
        return ret

    def write_list_as_line(self, the_list, entry_formatter=lambda s:s):
        """
        Writes the given list into a json line, where it is checked, if the list entries
        need to be rounded with quotes.
        Formats each list entry with the entry formatter.
        """
        line = [entry_formatter(self._in_quotes_if_necessary(v)) for v in the_list]
        return self.write_array_row(line)

    def write_objs(self, *objs):
        """
        Writes the params array of objs (in json format) as a json array.
        """
        return self.write_obj_from_lines(objs, left_envolop="[", right_envolop="]")

    def write_obj_from_lines(self, lines, left_envolop="{", right_envolop="}",
                             new_line_separator=",\n", left_new_line_envolop=True,
                             right_new_line_envolop=True):
        """
        Writes the given lines as separated string with the 'new_line_separator',
        with left and right envolop signs. Adds a new line at the end,
        if not 'right_new_line_envolop' is set to false.
        Using the default values, this method writes the lines (which should be in json format) as an
        json object.
        Using left_envolop = "[", right_envolop = "]" wites the lines as a json array.

        Returns a json string.
        """
        left = left_envolop + "\n" if left_new_line_envolop else left_envolop
        right = "\n" + right_envolop if right_new_line_envolop else right_envolop
        return left + new_line_separator.join(lines) + right

    def write_array_row(self, row_list):
        """
        Writes the row list of json strings as an array in one line.
        Returns a json string
        """
        return self.write_obj_from_lines(row_list, "\t[", "]", ", ", False, False)

    def write_json_from_rows(self, rows, col_width):
        """
        Writes an array of rows as json, where the col width is set to col_width signs.
        :param rows:
        :param col_width:
        :param json_writer:
        :return:
        """
        lines = []
        formatter = lambda s: s.ljust(col_width)
        for row in rows:
            lines.append("\t" + self.write_list_as_line(row, formatter))
        return self.write_obj_from_lines(lines, left_envolop="[", right_envolop="\t]")

    def write_datarange_from_rows(self, rows, entry_len):
        lines = []
        formatter = lambda s: s.ljust(entry_len)
        for row in rows:
            lines.append("\t" + self.write_list_as_line(row, formatter))
        return self.write_obj_from_lines(lines, left_envolop="[", right_envolop="\t]")

    def _in_quotes_if_necessary(self, value):
        if isinstance(value, bool):
            return self._in_quotes_if_necessary(str(value))
        if JSONWriter._is_a_number(value):
            return str(value)
        return '"' + str(value) + '"'

    @staticmethod
    def _is_a_number(value):
        if isinstance(value, (float, int)):
            return True
        '''
        if isinstance(value, str):
            val = value
            if val.startswith("-"):
                val = val[1:]
            val = val.replace(".", "")
            if val.isdigit():
                return True
        '''
        return False
