"""
This module contains a simple virtual table library for python similar to an excel spreadsheet.
The VTable class is used to create a 2 dimensional matrix which can be used to store/modify/export data in cells
  referenced by their column and row names.
Think of the VTable object like a BINGO sheet, to reference the cell value you would use table_variable['B', '3']
"""
import json
import csv
import StringIO


class VRow(object):
    """
    A dictionary wrapper object used to maintain index integrity as well as store column values for a row.
    Use just like a dictionary.

    Usage:
        >>> vr = VRow(['1', '2', '3'], 'test row header')
        >>> print vr['1']
        >>> # test row header
        >>> for column in vr:
        >>>     print column
        >>> # test row header
        >>> # None
        >>> # None
        >>> vr['3'] = 'test value'
        >>> print vr
        >>> # ['test row header', None, 'test value']
    """

    def __init__(self, column_headers, row_header, index=0):
        """

        :param column_headers: A list of the column headers used in your table.
        :param row_header: The hashable object used as the row header for this row.
        :param index: Used to maintain ordering integrity when displaying the table.
        """
        self._d = {header: dict(value=None, index=i) for i, header in enumerate(column_headers)}
        self._set_header(row_header)
        self.index = index

    def _convert(self, val, replacement):
        """
        Used when to_text is called to remove any unicode decode errors and convert the val to a string so that
        String.join() can be called on a list of the values for each column in this row.
        :param val: The value to convert to a string
        :param replacement: The replacement character for any NoneType objects
        :return: The string value of the val param
        """
        if val is None:
            return replacement
        if isinstance(val, str):
            return val
        return str(val)

    def as_list(self):
        """
        Return the contents of the row as a list. The internal dictionary is sorted by the index key to maintain
            ordering integrity.
        :return: list
        """
        return [v['value'] for k, v in sorted(self._d.items(), key=lambda x: x[1]['index'])]

    def as_dict(self):
        """
        Return the contents of the row as a dictionary with the key being the column name and the value being
            the row's column's value.
        :return:
        """
        d = {k: v['value'] for k, v in self._d.items()}
        d.update({'_index': self.index})
        return d

    def as_text(self, delim, none_value_replacement=''):
        """
        Return the contents of the row as a text delimited string.
        :param delim: The delimiter to use to separate the column values of this row.
        :param none_value_replacement: The replacement character to replace NoneType objects with.
        :return:
        """
        return delim.join([self._convert(x, none_value_replacement) for x in self.as_list()])

    @property
    def header(self):
        """
        Return the row header.
        :return:
        """
        return self.as_list()[0]

    def _set_header(self, header):
        """
        Set the row header.
        :param header: The hashable object to use as this rows header value.
        :return:
        """
        header_key = sorted(self._d.items(), key=lambda x: x[1]['index'])[0][0]
        self._d[header_key]['value'] = header

    def __iter__(self):
        return self.as_list().__iter__()

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.as_list())

    def __getitem__(self, item):
        return self._d[item]['value']

    def __setitem__(self, key, value):
        self._d[key]['value'] = value


class VTable(object):

    def __init__(self, column_headers, row_headers):
        """
        :type column_headers: list
        :type row_headers: list
        :param column_headers: A list of column_headers.
        :param row_headers: A list of row headers.
        """
        self.column_headers = column_headers
        self.row_headers = row_headers
        self.table_data = {}
        for i, row_header in enumerate(self.row_headers):
            if row_header not in self.table_data:
                self.table_data[row_header] = VRow(column_headers, row_header, i)
            else:
                raise ValueError('Row Header "{}" already in table'.format(row_header))

    @property
    def rows(self):
        """
        Return all rows in the table.
        :return:
        """
        return self.table_data.values()

    @property
    def columns(self):
        """
        Return all columns in the table.
        :return:
        """
        l = []
        for header in self.column_headers:
            d = []
            d.append(header)
            for row in self.table_data.values():
                d.append(row[header])
            l.append(d)
        return l

    def get_row(self, row_header):
        """
        Get a row by it's row header.
        :param row_header:
        :return:
        """
        return self.table_data[row_header]

    def _key_in_column_headers(self, key):
        return key in self.column_headers

    def _key_in_row_headers(self, key):
        return key in self.table_data

    def fill_column(self, column_name, value):
        """
        Fill a column in every row with a value.
        :param column_name: The column to fill.
        :param value: The value to fill the column with.
        :return:
        """
        for row in self.table_data.values():
            row[column_name] = value

    def export(self, delimiter, include_headers=True, none_replacement='', newline_char='\n'):
        """
        Export the table data into a human readable format.
        :param delimiter: The character to use as a delimiter to separate the values of each row.
        :param include_headers: Include the table headers in the exported data.
        :param none_replacement: The character to use to replace NoneType objects.
        :return: A human readable format of this table instance.
        """
        data = ''
        if include_headers:
            data += delimiter.join(self.column_headers)
            data += newline_char
        text_rows = []
        for row in sorted(self.table_data.values(), key=lambda x: x.index):
            text_rows.append(row.as_text(delimiter, none_replacement))
        data += newline_char.join(text_rows)
        return data

    def get_cell_value(self, column_header, row_header):
        """
        Get the cell value at the intersection of the column header and the row header.

        This method is the same as using my_table['column', 'row'].
        :param column_header:
        :param row_header:
        :return:
        """
        if column_header not in self.column_headers:
            raise KeyError("'{}' not in column headers.".format(column_header))
        if row_header not in self.table_data:
            raise KeyError("'{}' not in row headers.".format(row_header))
        return self.table_data[row_header][column_header]

    def set_cell_value(self, column_header, row_header, value):
        """
        Set the cell value at the intersection of the column header and the row header.

        This method is the same as using my_table['column', 'row'] = 'value'
        :param column_header:
        :param row_header:
        :param value:
        :return:
        """
        if column_header not in self.column_headers:
            raise KeyError("'{}' not in column headers.".format(column_header))
        if row_header not in self.table_data:
            raise KeyError("'{}' not in row headers.".format(row_header))
        if row_header == self.table_data[row_header][column_header]:
            raise AttributeError("Attempted to overwrite row header.")
        self.table_data[row_header][column_header] = value

    def json_serialize(self):
        """
        Serialize the table to a json format to be reopened with from_serialized_json().
        :return:
        """
        table_data = {}
        for k, v in self.table_data.items():
            table_data[k] = v.as_dict()
        d = {'table_data': table_data, 'row_headers': self.row_headers, 'column_headers': self.column_headers}
        return json.dumps(d)

    @classmethod
    def from_serialized_json(cls, json_string):
        d = json.loads(json_string)
        column_headers = d['column_headers']
        row_headers = d['row_headers']
        table_data = d['table_data']
        td = {}
        for k, v in table_data.items():
            td[k] = VRow(column_headers, k)
            for k1, v1 in v.items():
                if k1 == '_index':
                    td[k].index = v1
                    continue
                td[k][k1] = v1
        table = cls('', '')
        table.column_headers = column_headers
        table.row_headers = row_headers
        table.table_data = td
        return table

    @classmethod
    def from_iterable(cls, iterable):
        column_headers = iterable.pop(0)
        row_headers = [x[0] for x in iterable]
        td = {}
        for i, row in enumerate(iterable):
            vr = VRow(column_headers, row[0], i)
            for header, value in zip(column_headers, row):
                vr[header] = value
            td[row[0]] = vr
        table = cls('', '')
        table.column_headers = column_headers
        table.row_headers = row_headers
        table.table_data = td
        return table

    @classmethod
    def load_flat_file(cls, file_contents, delim):
        lines = [y.split(delim) for y in [x.strip('\r') for x in file_contents.split('\n')]]
        return cls.from_iterable(lines)

    @classmethod
    def load_csv(cls, file_contents, delimiter=','):
        io = StringIO.StringIO(file_contents)
        lines = list(csv.reader(io, delimiter=delimiter))
        return cls.from_iterable(lines)

    def __getitem__(self, item):
        column_header = item[0]
        row_header = item[1]
        return self.get_cell_value(column_header, row_header)

    def __setitem__(self, key, value):
        column_header = key[0]
        row_header = key[1]
        self.set_cell_value(column_header, row_header, value)

    def __iter__(self):
        return self.table_data.values().__iter__()


def run_test():
    # 'row_headers' as the first element is used to offset the row headers so that the value of the
    # 'A' column is not the row headers and can be filled in with a value later
    table = VTable(['row_headers', 'A', 'B', 'C', 'D', 'E'], ['1', '2', '3', '4', '5'])
    table['A', '1'] = 'X'
    table['B', '2'] = 'X'
    table['C', '3'] = 'X'
    table['D', '4'] = 'X'
    table['E', '5'] = 'X'
    print table.export('\t')
    print table.columns
    print table.rows
    for row in table:
        print row
        for column in row:
            print column

    # Dump and load to/from json
    tbl = table.from_serialized_json(table.json_serialize())
    print tbl.export('\t')


if __name__ == '__main__':
    run_test()
