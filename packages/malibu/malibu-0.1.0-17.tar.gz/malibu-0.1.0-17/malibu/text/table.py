#!/usr/bin/env python2.7

class TextTable(object):

    TABLE_CORNER = "+"
    TABLE_VT_BORDER = "|"
    TABLE_HZ_BORDER = "-"

    def __init__(self, min_width = 12):

        self.min_width = min_width

        self._rows = 0
        self._columns = 0

        # Header data should be simple; it should be no more than a list of 
        # strings naming each column header.
        self._header_data = []

        # Row data should be internally stored in a zipped-set form, or, as a
        # list of tuples, which each tuple containing all the entries for a 
        # single row.
        self._row_data = []

    def add_header_list(self, el):

        if not isinstance(el, list): return

        self._columns = len(el)
        self._header_data = el

    def add_header(self, *args):

        self._columns = len(args)
        self._header_data = [arg for arg in args]

    def add_data_dict(self, el):

        """ add_data_dict only really makes sense to use when there is a 
            single pair mapping (eg., key, value) or a two column
            display.  If that is not that case, add_data_ztup is a better
            choice. """

        if not isinstance(el, dict): return

        self._rows = len(el)

        for key, value in el.iteritems():
            self._row_data.append((key,value,))

    def add_data_ztup(self, el):

        """ add_data_ztup will take any as much data as you need and can even 
            fill the place of add_data_dict.  add_data_ztup takes a list of tuples.
            each tuple should contain a row of elements, one element for each column.
            essentially, the argument that will be passed in should look like:
              [
                (x1, y1, z1),
                (x2, y2, z2),
                    ...
                (xn, yn, zn)
              ] """

        if not isinstance(el, list): return

        self._rows = len(el)

        for row in el:
            if len(row) > self._columns:
                row = row[0:self._columns - 1]
            elif len(row) < self._columns:
                col_diff = (self._columns - len(row)) + 1
                col_fill = len(row)
                for idx in xrange(col_fill, col_diff):
                    el[idx] = ''
            self._row_data.append(row)

    def add_data_kv(self, k, v):

        """ add_data_kv is a simplified add_data_dict for pushing a data pair onto the
            row list on-the-fly. only effective for two-column data sets. """

        self._row_data.append((k, v,))

    def add_data_list(self, el):

        """ add_data_list adds a list of data to the table. this is primarily
            suitable for single-column data sets. """

        [self._row_data.append((elm,)) for elm in el]

    def add_data_csv_file(self, fobj):

        """ add_data_csv_file loads data from a comma-separated value file.  the first
            row is the header, everything else is actual data.  works if the file is
            provided or if a string containing the filename is given. """

        if isinstance(fobj, str):
            try: fobj = open(fobj, 'r')
            except: raise
        
        data_flag = False

        for line in fobj.readlines():
            line = line.strip().split(",")
            if not data_flag:
                self._columns = len(line)
                self.add_header_list(line)
                data_flag = True
                continue
            self.add_data_list(line)

    def __transpose_list(self, li):
        
        """ performs a simple transposition on a list. """

        return map(list, zip(*li))

    def __calculate_row_max(self):

        """ calculates the max size of the rows so the table has uniform column sizes. """

        __sizes = []

        for row in self._row_data + self._header_data:
            __sizes.append([len(el) for el in row])

        __sizes = self.__transpose_list(__sizes)

        return [max(cols) for cols in __sizes]

    def __format_divider(self):

        """ returns the table divider. """

        s = ""
        col_sizes = self.__calculate_row_max()

        for size in col_sizes:
            s += TextTable.TABLE_CORNER
            if size >= self.min_width:
                s += (TextTable.TABLE_HZ_BORDER * size)
            else:
                s += (TextTable.TABLE_HZ_BORDER * self.min_width)
        s += TextTable.TABLE_CORNER

        return s

    def __pad_left(self, txt, length):

        """ pads a string to be length characters long, from left. """

        s = []

        if len(txt) < length:
            diff = length - len(txt) - 1
            [s.append(" ") for i in xrange(0, diff)]
            s.append(txt + " ")
        elif len(txt) == length:
            s.append(txt)

        return ''.join(s)

    def __format_header_data(self):

        """ formats the header data. """

        lines = []
        col_sizes = self.__calculate_row_max()

        line = ""
        
        cd = zip(self._header_data, col_sizes)
        for (text, size) in cd:
            if size < self.min_width:
                size = self.min_width
            text = self.__pad_left(text, size)
            line += TextTable.TABLE_VT_BORDER
            line += text
        line += TextTable.TABLE_VT_BORDER
        lines.append(line)

        return lines

    def __format_table_data(self):

        """ formats the table data. """

        lines = []
        col_sizes = self.__calculate_row_max()

        for row in self._row_data:
            rd = zip(row, col_sizes)
            line = ""
            for (text, size) in rd:
                if size < self.min_width:
                    size = self.min_width
                text = self.__pad_left(text, size)
                line += TextTable.TABLE_VT_BORDER
                line += text
            line += TextTable.TABLE_VT_BORDER
            lines.append(line)

        return lines

    def format(self):

        """ format the table and return the string. """

        lines = []
        divider = self.__format_divider()

        lines.append(divider)
        [lines.append(line) for line in self.__format_header_data()]
        lines.append(divider)
        [lines.append(line) for line in self.__format_table_data()]
        lines.append(divider)

        return lines

