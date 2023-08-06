import os
import xlwt
import xlrd
from collections import defaultdict
from collections import OrderedDict
from spanner import countdown


class ExcelTable(object):
    # keep formatting objects in a dictionary; otherwise, each instance is
    # treated as a separate entity by excel, which eventually (limit 4k)
    # gives up trying to interpret them.
    easyxfs = dict()
    easyxfs['bold'] = xlwt.easyxf('font: bold 1')
    easyxfs['bold+rotate'] = xlwt.easyxf('font: bold 1; align: rotation 90')
    easyxfs['hyperlink'] = xlwt.easyxf('font: colour blue, underline on')
    easyxfs[None] = xlwt.easyxf('font: colour black')

    def __init__(self, sheetname=None, colnames=None, header_format='bold'):
        self.book = xlwt.Workbook()
        self.name_to_sheet = dict()
        self.sheet_to_colnames = dict()
        self.sheet_to_rownum = defaultdict(int)
        if sheetname is not None:
            self.add_sheet(sheetname, colnames, header_format)

    def add_sheet(self, sheetname, colnames, header_format='bold'):
        if sheetname not in self.name_to_sheet:
            sheet = self.book.add_sheet(sheetname)
            self.name_to_sheet[sheetname] = sheet
            self.sheet_to_colnames[sheet] = colnames
            self.add_row(colnames, header_format, sheetname)
        else:
            print 'Sheet "%s" already exists' % sheetname

    def add_row(self, values, cell_formats=None, sheetname=None):
        if sheetname is None:
            assert len(self.name_to_sheet) == 1, 'Please specify a sheet name'
            sheet = self.name_to_sheet.values()[0]
        else:
            assert sheetname in self.name_to_sheet, \
                'Sheet "%s" has not yet been created.' % sheetname
            sheet = self.name_to_sheet[sheetname]

        assert len(values) == len(self.sheet_to_colnames[sheet]), \
            'Please provide a value for each column: %s' % \
            self.sheet_to_colnames[sheet]

        if not isinstance(cell_formats, list):
            cell_formats = [cell_formats] * len(values)

        for idx, cell_format in enumerate(cell_formats):
            if cell_format in self.easyxfs:
                cell_formats[idx] = self.easyxfs[cell_format]
            elif not isinstance(cell_format, xlwt.Style.XFStyle):
                raise RuntimeError('Unexpected format "%s".  '
                                   'Please select from the following: %s'
                                   % sorted(str(self.easyxfs.keys())))

        row = self.sheet_to_rownum[sheet]
        self.sheet_to_rownum[sheet] += 1

        for (col, (val, cell_format)) in enumerate(zip(values, cell_formats)):
            sheet.write(row, col, val, cell_format)

    def write_to_file(self, filename):
        self.book.save(filename)


###############################################################################


class TabTable(object):
    def __init__(self, colnames, filename):
        self.ncols = len(colnames)
        self.ofh = open(filename, 'w')
        self.add_row(colnames)

    def add_row(self, values):
        if len(values) != self.ncols:
            print 'Please provide %d columns (provided: %d)' \
                  % (self.ncols, len(values))
            return

        def strip_non_ascii(x):
            if isinstance(x, unicode):
                return x.encode('ascii', 'ignore')
            elif isinstance(x, str):
                return str(unicode(x, 'ascii', 'ignore'))
            else:
                return str(x)

        self.ofh.write(
            '%s\n' % '\t'.join([strip_non_ascii(x) for x in values]))

    def close(self):
        if not self.ofh.closed:
            self.ofh.close()

    def __del__(self):
        self.close()

###############################################################################


def row_iterator(filename, selected_cols=None, delimiter='\t', no_header=False,
                 header_row=0, xls_sheetname=None, force_timer=False,
                 timer_label=None, as_dict=False):

    timer = init_timer(filename, force_timer, timer_label)

    def make_row_reader():
        if filename.split('.')[-1].lower() in ('xls', 'xlsx'):
            class ExcelRowReader(object):
                row = 0
                book = xlrd.open_workbook(filename)
                if xls_sheetname is not None:
                    sheet = book.sheet_by_name(xls_sheetname)
                else:
                    sheet = book.sheet_by_index(0)

                def next_row(self):
                    if self.row >= self.sheet.nrows:
                        return None

                    cols = [self.sheet.cell(self.row, col).value
                            for col in xrange(self.sheet.ncols)]
                    self.row += 1
                    return cols

            return ExcelRowReader()
        else:
            class FlatFileRowReader(object):
                fh = open(filename, 'r')

                def next_row(self):
                    line = self.fh.readline().rstrip('\r\n')
                    if len(line) > 0:
                        return line.split(delimiter)
                    else:
                        return None

                def __del__(self):
                    self.fh.close()

            return FlatFileRowReader()

    rr = make_row_reader()

    for _ in xrange(header_row):
        rr.next_row()

    columns = rr.next_row()
    if no_header:
        col_names = range(len(columns))
        if selected_cols is not None:
            col_indices = selected_cols
        else:
            col_indices = None
    else:
        col_names = columns
        # if no columns specified, get them all
        if selected_cols is None:
            col_indices = range(len(col_names))
        else:
            # if the columns are already specified as integer indices, there's
            # nothing further to do
            if all(map(lambda x: isinstance(x, int), selected_cols)):
                col_indices = selected_cols
            else:
                selected_cols = [x.lower() for x in selected_cols]
                col_names_lwr = [x.lower() for x in col_names]

                col_indices = []
                for col in selected_cols:
                    try:
                        col_indices.append(col_names_lwr.index(col))
                    except ValueError:
                        raise Exception('Column not found: ' + col +
                                        '\nAvailable columns: ' +
                                        str(col_names))

        columns = rr.next_row()

    if timer is not None:
        timer.tick()

    def cast_cell_value(value):
        if isinstance(value, str):
            x = str(unicode(value, 'ascii', 'ignore'))
            try:
                return int(x.replace(',', ''))
            except:
                try:
                    return float(x.replace(',', ''))
                except:
                    return x

        elif isinstance(value, unicode):
            return cast_cell_value(value.encode('ascii', 'ignore'))

        elif isinstance(value, float):
            if int(value) == value:
                return int(value)

        return value

    def select_cols(indices, values):
        if len(indices) == 1:
            return cast_cell_value(values[indices[0]])

        val = []
        for index in indices:
            value = cast_cell_value(values[index])
            val.append(value)

        return tuple(val)

    while columns:
        if col_indices is None:
            col_indices = range(len(columns))

        if len(columns) <= max(col_indices):
            print columns, col_indices
            print 'Warning - unexpected number of columns encountered.  ' \
                  'Returning current result.'
            break

        vals = select_cols(col_indices, columns)
        columns = rr.next_row()
        if timer is not None:
            timer.tick()

        if as_dict:
            yield OrderedDict((col_names[col_indices[i]], v)
                              for i, v in enumerate(vals))
        else:
            yield vals


def load_dict(filename, key_cols, val_cols, delimiter='\t',
              force_unique_keys=False, no_header=False, header_row=0,
              xls_sheetname=None, force_timer=False, timer_label=None):

    multiple_values_found_for_at_least_one_key = False

    d = dict()
    for kvps in row_iterator(filename, key_cols + val_cols,
                             delimiter=delimiter,
                             no_header=no_header,
                             header_row=header_row,
                             xls_sheetname=xls_sheetname,
                             force_timer=force_timer,
                             timer_label=timer_label,
                             as_dict=True):
        def get_vals(cols):
            if len(cols) == 1:
                return kvps[cols[0]]
            else:
                return tuple(kvps[col] for col in cols)

        key = get_vals(key_cols)
        val = get_vals(val_cols)

        if key in d:
            if force_unique_keys:
                raise RuntimeError("Non-unique key encountered: " + str(key))

            if type(d[key]) is not set:
                if val != d[key]:
                    multiple_values_found_for_at_least_one_key = True
                    d[key] = set([d[key]])
                    d[key].add(val)
            else:
                d[key].add(val)
        else:
            d[key] = val

    # force all values to lists if any key has multiple values
    if multiple_values_found_for_at_least_one_key:
        for key in d:
            if type(d[key]) is set:
                vals = list(d[key])
            else:
                vals = [d[key]]

            d[key] = []
            for vs in vals:
                if len(val_cols) > 1:
                    d[key].append({k: v for k, v in zip(val_cols, vs)})
                else:
                    d[key] = vals
    else:
        for key in d:
            if len(val_cols) > 1:
                d[key] = {k: v for k, v in zip(val_cols, d[key])}

    return d


def init_timer(filename, force_timer=False, timer_label=None):
    if not os.path.isfile(filename):
        raise Exception('File does not exist: ' + filename)

    # always show timer if file is over 1GB
    if force_timer or (force_timer is None and os.path.getsize(filename) > 1024 * 1024 * 1024):
        print 'Determining line count of %s...' % filename
        assert os.path.exists(filename), 'File does not exist: ' + filename
        with open(filename, 'r') as f:
            for i, line in enumerate(f):
                pass

            linecount = i + 1

        if timer_label is None:
            timer_label = 'Reading file: %s' % filename

        return countdown.timer(total_iterations=linecount, label=timer_label)

    return None
