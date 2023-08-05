"""
    pyexcel.ext.ods3
    ~~~~~~~~~~~~~~~~~~~

    ODS format plugin for pyexcel

    :copyright: (c) 2014 by C. W.
    :license: GPL v3
"""
import sys
import datetime
import ezodf
from collections import OrderedDict
import pkg_resources
from pyexcel_io import SheetReaderBase, BookReader, SheetWriter, BookWriter
if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import BytesIO as StringIO


def float_value(value):
    ret = float(value)
    return ret


def date_value(value):
    tokens = value.split('-')
    year = int(tokens[0])
    month = int(tokens[1])
    day = int(tokens[2])
    ret = datetime.date(year, month, day)
    return ret


def time_value(value):
    hour = int(value[2:4])
    minute = int(value[5:7])
    second = int(value[8:10])
    ret = datetime.time(hour, minute, second)
    return ret


def boolean_value(value):
    return value


ODS_FORMAT_CONVERSION = {
    "float": float,
    "date": datetime.date,
    "time": datetime.time,
    "boolean": bool,
    "percentage": float,
    "currency": float
}


VALUE_CONVERTERS = {
    "float": float_value,
    "date": date_value,
    "time": time_value,
    "boolean": boolean_value,
    "percentage": float_value,
    "currency": float_value
}


VALUE_TOKEN = {
    "float": "value",
    "date": "date-value",
    "time": "time-value",
    "boolean": "boolean-value",
    "percentage": "value",
    "currency": "value"
}

ODS_WRITE_FORMAT_COVERSION = {
    float: "float",
    int: "float",
    str: "string",
    datetime.date: "date",
    datetime.time: "time",
    bool: "boolean"
}


if sys.version_info[0] < 3:
    ODS_WRITE_FORMAT_COVERSION[unicode] = "string"


class ODSSheet(SheetReaderBase):
    @property
    def name(self):
        return self.native_sheet.name

    def to_array(self):
        """reads a sheet in the sheet dictionary, storing each sheet
        as an array (rows) of arrays (columns)"""
        table = []
        for row in range(self.native_sheet.nrows()):
            rows = []
            for column, cell in enumerate(self.native_sheet.row(row)):
                ret = self._read_cell(cell)
                rows.append(ret)
            # if row contained something
            table.append(rows)

        return table

    def _read_cell(self, cell):
        cell_type = cell.value_type
        ret = None
        if cell_type in ODS_FORMAT_CONVERSION:
            value = cell.value
            n_value = VALUE_CONVERTERS[cell_type](value)
            ret = n_value
        else:
            if cell.value is None:
                ret = ""
            else:
                ret = cell.value
        return ret


class ODSBook(BookReader):

    def getSheet(self, native_sheet):
        return ODSSheet(native_sheet)

    def load_from_file(self, filename):
        return ezodf.opendoc(filename)

    def load_from_memory(self, file_content):
        try:
            return ezodf.opendoc(None, file_content)
        except:
            raise NotImplementedError("Please use custom version of ezodf")

    def sheetIterator(self):
        return self.native_book.sheets


class ODSSheetWriter(SheetWriter):
    """
    ODS sheet writer
    """
    def set_sheet_name(self, name):
        self.native_sheet = ezodf.Sheet(name)
        self.current_row = 0

    def set_size(self, size):
        self.native_sheet.reset(size=size)

    def write_row(self, array):
        """
        write a row into the file
        """
        count = 0
        for cell in array:
            value_type = ODS_WRITE_FORMAT_COVERSION[type(cell)]
            if value_type == "time":
                cell = cell.strftime("PT%HH%MM%SS")
            self.native_sheet[self.current_row, count].set_value(
                cell,
                value_type=value_type)
            count += 1
        self.current_row += 1

    def write_array(self, table):
        rows = len(table)
        if rows > 0:
            columns = max(map(len, table))
        if columns == 0:
            return
        self.set_size((rows, columns))
        for row in table:
            self.write_row(row)

    def close(self):
        """
        This call writes file

        """
        self.native_book.sheets += self.native_sheet


class ODSWriter(BookWriter):
    """
    open document spreadsheet writer

    """
    def __init__(self, filename, **keywords):
        BookWriter.__init__(self, filename)  # in case something will be done
        self.native_book = ezodf.newdoc(doctype="ods", filename=filename)

    def create_sheet(self, name):
        """
        write a row into the file
        """
        return ODSSheetWriter(self.native_book, None, name)

    def close(self):
        """
        This call writes file

        """
        self.native_book.save()

try:
    from pyexcel.io import READERS
    from pyexcel.io import WRITERS

    READERS["ods"] = ODSBook
    WRITERS["ods"] = ODSWriter
except:
    # to allow this module to function independently
    pass

__VERSION__ = "0.0.6"
