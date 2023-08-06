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
from lxml import etree
from editpyxl.constants import SHEET_MAIN_NS

log = getLogger('editpyxl')


class Cell(object):
    """
    Sub-class for ExcelWorksheet, to allow similar interface to openpyxl, ie ws.cell().value
    """
    def __init__(self, worksheet, cell, name):
        self.ws = worksheet
        self.cell = cell
        self.name = name

    def get_shared_string(self, id):
        """Update a shared string from the shared string table and return the value.  Used by cell()."""
        ssXML = self.ws.wb.xmls['xl/sharedStrings.xml']
        el = ssXML.findall('{0}si'.format(SHEET_MAIN_NS))[id].find('{0}t'.format(SHEET_MAIN_NS))
        return el.text

    def set_shared_string(self, id, v):
        """Update a shared string from the shared string table and return the value.  Used by cell()."""
        ssXML = self.ws.wb.xmls['xl/sharedStrings.xml']
        el = ssXML.findall('{0}si'.format(SHEET_MAIN_NS))[id].find('{0}t'.format(SHEET_MAIN_NS))
        if v is not None:
            el.text = v
        else:
            el.text = ''

    @property
    def formula(self):
        """Value of a formula is the value of the cell"""
        return self.value

    @formula.setter
    def formula(self, v):
        """Update an excel formula, but don't change the value."""
        v = str(v) if v is not None else ''
        f_xml = self.cell.find('{0}f'.format(SHEET_MAIN_NS))
        if f_xml is not None:
            # Remove any existing formula when setting the value
            f_xml.text = v
        else:
            raise AttributeError('Unable to update cell {0} to {1} - check cell type.'.format(self.name, v))

    @property
    def select(self):
        """Value of select list comes from the string table in the same manner as a normal string"""
        return self.value

    @select.setter
    def select(self, v):
        """Update an excel cell and return the value.  If value is not specified, return the current cell value."""
        v = str(v) if v is not None else ''
        try:
            index = self.ws.wb.string_table.index(v)
        except ValueError:
            raise ValueError('Option not in string table: {0}'.format(v))
        if len(self.ws.select_options) and v not in self.ws.select_options[self.name]:
            raise ValueError('Option not available for {0}: {1}'.format(self.name, v))
        v_xml = self.cell.find('{0}v'.format(SHEET_MAIN_NS))
        if v_xml is not None:
            v_xml.text = str(index)
        else:
            raise AttributeError('Unable to update cell {0} to SELECT({1}) - check cell type.'.format(self.name, v))

    @property
    def value(self):
        """Get the value of a cell."""
        v_xml = self.cell.find('{0}v'.format(SHEET_MAIN_NS))
        if v_xml is not None:
            if 't' in self.cell.attrib and self.cell.attrib['t'] == 's':  # value is from string table
                sid = int(v_xml.text)
                return self.get_shared_string(sid)
            return v_xml.text
        return None

    @value.setter
    def value(self, v):
        """Update an excel cell and return the value.  If value is not specified, return the current cell value."""
        v = str(v) if v is not None else ''
        f_xml = self.cell.find('{0}f'.format(SHEET_MAIN_NS))
        if f_xml is not None:
            # Remove any existing formula when setting the value
            f_xml.getparent().remove(f_xml)
        v_xml = self.cell.find('{0}v'.format(SHEET_MAIN_NS))
        if v_xml is not None:
            if 't' in self.cell.attrib and self.cell.attrib['t'] == 's':  # value is from string table
                sid = int(v_xml.text)
                self.set_shared_string(sid, v)
            else:
                v_xml.text = v
        elif 't' not in self.cell.attrib or self.cell.attrib['t'] != 's':
            if hasattr(etree, 'Element'):
                v_xml = etree.Element('{0}v'.format(SHEET_MAIN_NS))
                v_xml.text = v
                self.cell.append(v_xml)
                log.warn('Appending new value on {0} = {1}'.format(self.name, v))
            else:
                raise AttributeError('Unable to update cell {0} to {1} - etree error.'.format(self.name, v))
        else:
            raise AttributeError('Unable to update cell {0} to {1} - check cell type.'.format(self.name, v))