import os
import atexit
import xlwt
from collections import defaultdict

# keep formatting objects in a dictionary; otherwise, each instance is treated as a separate entity by excel,
# which eventually (limit 4k) gives up trying to interpret them.
easyxfs = dict()
easyxfs['bold'] = xlwt.easyxf('font: bold 1')
easyxfs['bold+rotate'] = xlwt.easyxf('font: bold 1; align: rotation 90')
easyxfs['hyperlink'] = xlwt.easyxf('font: colour blue, underline on')
easyxfs[None] = xlwt.easyxf('font: colour black')


class ExcelTable(object):
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
            assert sheetname in self.name_to_sheet, 'Sheet "%s" has not yet been created.' % sheetname
            sheet = self.name_to_sheet[sheetname]

        assert len(values) == len(self.sheet_to_colnames[sheet]), 'Please provide a value for each column: %s' % self.sheet_to_colnames[sheet]

        if not isinstance(cell_formats, list):
            cell_formats = [cell_formats] * len(values)

        for idx, cell_format in enumerate(cell_formats):
            if cell_format in easyxfs:
                cell_formats[idx] = easyxfs[cell_format]
            elif not isinstance(cell_format, xlwt.Style.XFStyle):
                raise RuntimeError('Unexpected format "%s".  Please select from the following values: %s' % sorted(str(easyxfs.keys())))

        row = self.sheet_to_rownum[sheet]
        self.sheet_to_rownum[sheet] += 1

        for (col, (val, cell_format)) in enumerate(zip(values, cell_formats)):
            sheet.write(row, col, val, cell_format)

    def write_to_file(self, filename):
        self.book.save(filename)


class HTMLtable(object):
    def __init__(self, colnames, header_color='White'):
        with open(os.path.join(os.path.dirname(__file__), 'template.html'), 'r') as fh:
            self.template = fh.read()

        self.ncols = len(colnames)
        self.table_rows = ['<tr bgcolor="%s"><th>%s</th></tr>' %
                            (header_color, '</th><th>'.join([str(c) for c in colnames]))]

    def add_row(self, values, row_color='White'):
        if len(values) != self.ncols:
            print 'Please provide %d columns (provided: %d)' % (self.ncols, len(values))
            return

        self.table_rows.append('<tr bgcolor="%s"><td>%s</td></tr>' % (row_color, '</td><td>'.join([str(v) for v in values])))

    def write_to_file(self, filename):
        html = self.template.replace('{TABLE_CONTENTS}', '\n'.join(self.table_rows))
        with open(filename, 'w') as ofh:
            ofh.write(html)


class TabTable(object):
    def __init__(self, colnames, filename):
        self.ncols = len(colnames)
        self.ofh = open(filename, 'w')
        self.add_row(colnames)

    def add_row(self, values):
        if len(values) != self.ncols:
            print 'Please provide %d columns (provided: %d)' % (self.ncols, len(values))
            return

        def strip_non_ascii(x):
            if isinstance(x, unicode):
                return x.encode('ascii', 'ignore')
            elif isinstance(x, str):
                return str(unicode(x, 'ascii', 'ignore'))
            else:
                return str(x)

        self.ofh.write('%s\n' % '\t'.join([strip_non_ascii(x) for x in values]))

    def __del__(self):
        if not self.ofh.closed:
            self.ofh.close()

