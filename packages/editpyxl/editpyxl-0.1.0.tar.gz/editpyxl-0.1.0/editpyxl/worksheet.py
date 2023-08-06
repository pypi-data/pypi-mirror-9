# Copyright (c) 2014 editpyxl
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# @license: http://www.opensource.org/licenses/mit-license.php
# @author: see AUTHORS file

from logging import getLogger
from editpyxl.util import OrderedSet
from editpyxl.constants import SHEET_MAIN_NS, CELL_RE, COLUMN_RE
from editpyxl.cell import Cell

log = getLogger('editpyxl')


class Worksheet(object):
    """
    Sub-class for ExcelWorkbook, to allow similar interface to openpyxl, ie ws = wb.get_sheet_by_name('Sheet1')
    """
    def __init__(self, workbook, xmlKey, name):
        self.wb = workbook
        self.xmlKey = xmlKey
        self.id = int(xmlKey[19:-4])  # 'xl/worksheets/sheet1.xml' -> 1
        self.name = name
        self._cells = {}
        self.select_options = {}

    def cell(self, coordinate=None, row=None, column=None):
        """
        Return a cell for a coordinate.  Note - as of v2.0, openpyxl uses a 1-based row,col system, so row=1, col=1
        is cell A1.
        """
        if not coordinate:
            coordinate = self.row_col_to_cell(row, column)
        else:
            row, column = self.cell_to_row_col(coordinate)
        if coordinate not in self._cells:
            xml = self.wb.xmls[self.xmlKey]
            c = xml.find('{0}sheetData/{0}row[@r="{1}"]/{0}c[@r="{2}"]'.format(SHEET_MAIN_NS, row, coordinate))
            if c is None:
                raise IndexError('Cell {0} on {1} does not exist'.format(coordinate, self.name))
            else:
                self._cells[coordinate] = Cell(self, c, coordinate)
        return self._cells[coordinate]

    @staticmethod
    def cell_to_row_col(ref):
        """Break an excel cell reference such as A1 into it's row and column components"""
        col_row = CELL_RE.match(ref.upper()).groups()
        return int(col_row[1]), Worksheet.col_number(col_row[0])

    @staticmethod
    def col_name(col):
        """Convert excel column integer index to letter"""
        letters = []
        while col > 0:
            col, remainder = divmod(col, 26)
            if remainder == 0:
                remainder = 26
                col -= 1
            letters.append(chr(remainder+64))
        return ''.join(reversed(letters))

    @staticmethod
    def col_number(col):
        """Convert excel column letter to integer index"""
        m = COLUMN_RE.match(col.upper())
        idx = 0
        for i, l in enumerate(reversed(m.group(0))):
            idx += (ord(l) - 64) * pow(26, i)
        return idx

    @staticmethod
    def row_col_to_cell(row, col):
        """Translate a row, col a cell reference."""
        return '{0}{1}'.format(Worksheet.col_name(col), row)

    @staticmethod
    def cells_in_range(cell_range, include_2d=True):
        """
        Returns the cell name for each cell in a given range.  If include_2d=False, then ignore ranges which span
        multiple rows and columns.  An individual cell will be returned as itself.  Multiple ranges will be parsed
        if separated by a space.
        """
        cells = OrderedSet()
        rangeSets = cell_range.split(' ')
        for rs in rangeSets:
            if len(rs.split(':')) > 1:
                try:
                    start_row, start_col = Worksheet.cell_to_row_col(rs.split(':')[0])
                    end_row, end_col = Worksheet.cell_to_row_col(rs.split(':')[1])
                    if include_2d or (end_row - start_row == 0 or end_col - start_col == 0):
                        # If include_2d=False ignore matricies.  Used for ensuring validating select lists.
                        for r in range(start_row, end_row + 1):
                            for c in range(start_col, end_col + 1):
                                cells.add(Worksheet.row_col_to_cell(r, c))
                except AttributeError:
                    continue
            else:
                # Just add individual cell
                cells.add(rs)
        return list(cells)

    def validate_select_options(self):
        """
        If called, the worksheet will validate select options before they're set to ensure they are setting a correct
        value.
        """
        if not len(self.wb.defined_names):
            self.wb.load_defined_names()

        xml = self.wb.xmls[self.xmlKey]
        dv = xml.findall('{0}dataValidations/{0}dataValidation'.format(SHEET_MAIN_NS))
        cells_to_range_map = [(el.attrib['sqref'], el.find('{0}formula1'.format(SHEET_MAIN_NS)).text) for el in dv]
        self.select_options = {}
        for cell_range, named_range in cells_to_range_map:
            # cell_range are the cells on the sheet with select lists
            # named_range is the defined name which contains the range of cells for the options
            self.select_options.update({c: self.wb.defined_names[named_range]
                                        for c in self.cells_in_range(cell_range)})

        return self
