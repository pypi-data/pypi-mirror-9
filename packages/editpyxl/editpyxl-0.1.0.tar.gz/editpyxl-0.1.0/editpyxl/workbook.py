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
from uuid import uuid1
from os.path import exists, join, basename
from os import remove, makedirs
from shutil import copyfile, rmtree, move
from tempfile import mkdtemp
from zipfile import ZipFile
from lxml import etree
from editpyxl.constants import SHEET_MAIN_NS, RELATIONSHIPS_NS
from editpyxl.worksheet import Worksheet

log = getLogger('editpyxl')


class Workbook(object):
    """
    Fast XML interface to editing an excel workbook.  Limited in ability to update (can't create new cells), but
    but designed to be fast and efficient.  API mirrors openpyxl where possible.
    """
    def __init__(self):
        self.workFolder = mkdtemp()
        self.zip = None
        self.uuid = uuid1().get_hex()
        self.path = join(self.workFolder, 'xml-{0}'.format(self.uuid))
        self.xmls = {}  # {filename in zip: loaded lxml object}
        self.sheet_id = {}  # Map to loaded xml's - {name: filename in zip}
        self.string_table = []  # A copy of the string table for finding the index of a string.
        self.defined_names = {}
        self.active_sheet_index = 0

    def __del__(self):
        self.close()
        rmtree(self.workFolder)

    @property
    def active(self):
        """Get the active sheet"""
        sheet_names = self.get_sheet_names()
        if 0 <= self.active_sheet_index < len(sheet_names):
            return self.get_sheet_by_name(sheet_names[self.active_sheet_index])
        else:
            return sheet_names[0]

    @active.setter
    def active(self, value):
        """Set the active sheet"""
        self.active_sheet_index = value

    def close(self):
        """Delete the xml-uuid path and all files in it."""
        if exists(self.path):
            rmtree(self.path)
        self.zip = None
        self.xmls = {}
        self.sheet_id = {}
        self.string_table = []
        self.defined_names = {}
        self.active_sheet_index = 0
        return self

    def get_sheet_by_name(self, name):
        """Load an excel sheet with the specific sheet name.  If the shared strings is not loaded, load this as well."""
        sheetFilename = self.sheet_filename(name)
        self.load_XML(sheetFilename)
        self.sheet_id[name] = sheetFilename
        return Worksheet(self, sheetFilename, name)

    def get_sheet_names(self):
        """Return a list of sheet names"""
        sheetEls = self.xmls['xl/workbook.xml'].findall('{0}sheets/{0}sheet'.format(SHEET_MAIN_NS))
        return [el.attrib['name'] for el in sheetEls]

    def hide_sheet(self, name):
        """Hide an excel sheet."""
        sheet_xml = self.xmls['xl/workbook.xml'].find('{0}sheets/{0}sheet[@name="{1}"]'.format(SHEET_MAIN_NS, name))
        if sheet_xml is not None:
            sheet_xml.attrib['state'] = 'hidden'

    def unhide_sheet(self, name):
        """Unhide an excel sheet."""
        sheet_xml = self.xmls['xl/workbook.xml'].find('{0}sheets/{0}sheet[@name="{1}"]'.format(SHEET_MAIN_NS, name))
        if sheet_xml is not None:
            sheet_xml.attrib.pop('state', None)

    def load_XML(self, filename):
        """Load an xml file.  Assumes the filename has been opened, or exists in the zip file."""
        if isinstance(self.zip, ZipFile):
            try:
                self.zip.extract(filename, self.path)
            except KeyError:
                log.warn('Excel file does not contain {0}'.format(filename))
                return self
        if hasattr(etree, 'parse'):
            xml = etree.parse(join(self.path, filename))
            self.xmls[filename] = xml
        return self

    def load_defined_names(self):
        """
        Load values for defined names in a workbook.

        Note - ignores defined_names for matricies to avoid large data and complex ranges for print ranges.  Could
        also filter on name = _xlnm.Print_Area.
        """
        xml = self.xmls['xl/workbook.xml']
        dn = xml.findall('{0}definedNames/{0}definedName'.format(SHEET_MAIN_NS))
        sheet_names = self.get_sheet_names()
        raw_names = [(el.text.split('!')[0], el.attrib['name'], el.text.split('!')[1].replace('$', ''))
                     for el in dn if el.text.split('!')[0] in sheet_names]
        defined_ranges = {sheet: {} for sheet in sheet_names}
        for sheet, key, range in raw_names:
            cells = Worksheet.cells_in_range(range, False)  # Skip 2d ranges - usually print ranges
            if len(cells):
                defined_ranges[sheet][key] = cells

        for sheet in defined_ranges.keys():
            if not len(defined_ranges[sheet]):
                defined_ranges.pop(sheet, None)

        self.defined_names = {}
        for sheet in defined_ranges.keys():
            ws = self.get_sheet_by_name(sheet)
            for name, cells in defined_ranges[sheet].items():
                options = [ws.cell(c).value for c in cells]
                self.defined_names[name] = options if len(options) > 1 else options[0]

        return self

    def open(self, srcFilename):
        """Open an excel file (xlsx or xlsm) and load the string table and workbook xmls."""
        self.close()  # Start fresh

        # Load a local copy of the zip file and attach it to self.zip
        if not exists(self.path):
            makedirs(self.path)
        destFilename = join(self.path, basename(srcFilename))
        if exists(destFilename):
            remove(destFilename)
        copyfile(srcFilename, destFilename)
        self.zip = ZipFile(destFilename, 'r')

        # Load the shared strings and populate the string table
        self.load_XML('xl/sharedStrings.xml')
        xml = self.xmls.get('xl/sharedStrings.xml', None)
        self.string_table = []
        if xml:
            for siEl in xml.findall('{0}si'.format(SHEET_MAIN_NS)):
                tEl = siEl.find('{0}t'.format(SHEET_MAIN_NS))
                if tEl is not None:
                    self.string_table.append(tEl.text)
                else:
                    self.string_table.append('')
        # Load the workbook
        self.load_XML('xl/workbook.xml')
        xml = self.xmls['xl/workbook.xml']
        view = xml.find('*/' '{0}workbookView'.format(SHEET_MAIN_NS))
        if view is not None and 'activeTab' in view.attrib:
            self.active = int(view.attrib['activeTab'])

        # Set the full recalc flag.
        calcPr = self.xmls['xl/workbook.xml'].find('{0}calcPr'.format(SHEET_MAIN_NS))
        calcPr.set('fullCalcOnLoad', '1')

        return self

    @staticmethod
    def remove_from_zip(zipfname, filenames):
        """
        Remove a file from a zip.  Required to overwrite a file in an existing archive.  Since ZipFile lacks the
        ability, this basically creates a new zip file without the files.
        """
        tempdir = mkdtemp()
        try:
            tempname = join(tempdir, 'new.zip')
            with ZipFile(zipfname, 'r') as zipread:
                with ZipFile(tempname, 'w') as zipwrite:
                    for item in zipread.infolist():
                        if item.filename not in filenames:
                            data = zipread.read(item.filename)
                            zipwrite.writestr(item, data)
            move(tempname, zipfname)
        finally:
            rmtree(tempdir)

    def sheet_filename(self, name):
        """Find an excel sheet filename, i.e. translate a sheet name into the correct xl/worksheet/sheet1.xml"""
        sheet_xml = self.xmls['xl/workbook.xml'].find('{0}sheets/{0}sheet[@name="{1}"]'.format(SHEET_MAIN_NS, name))
        if sheet_xml is not None:
            sheet = sheet_xml.attrib
            return 'xl/worksheets/sheet{0}.xml'.format(sheet['{0}id'.format(RELATIONSHIPS_NS)][3:])
        else:
            log.warn('Unknown sheet: {0}'.format(name))
            return None

    def save(self, fullFilename):
        """Update the loaded zip file and save back to an excel file."""
        if isinstance(self.zip, ZipFile):
            # Write the loaded xml files back to their files
            for filename, doc in self.xmls.items():
                output = open(join(self.path, filename), 'w')
                doc.write(output)
                output.close()

            # Write the zip file
            zipFilename = self.zip.filename
            self.zip.close()
            remove_list = self.xmls.keys()
            remove_list.append('xl/calcChain.xml')  # Force excel to recreate to avoid errors.
            self.remove_from_zip(zipFilename, remove_list)
            updateZip = ZipFile(zipFilename, 'a')
            for filename in self.xmls.keys():
                updateZip.write(join(self.path, filename), filename)
            updateZip.close()
            self.zip = ZipFile(zipFilename, 'r')

            copyfile(self.zip.filename, fullFilename)
            return fullFilename
        return None