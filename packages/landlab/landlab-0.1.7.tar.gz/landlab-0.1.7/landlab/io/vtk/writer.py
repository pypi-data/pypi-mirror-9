#! /bin/env python
import os
import xml.dom.minidom


_VALID_ENCODINGS = set(['ascii', 'base64', 'raw'])
_VALID_FORMATS = set(['ascii', 'base64', 'raw', 'appended'])
_VTK_POSSIBLE_PIECE_SECTIONS = [
    'Points', 'Coordinates', 'PointData', 'Cells', 'CellData',
]


class VtkError(Exception):
    pass


class InvalidFormatError(VtkError):
    def __init__(self, format_str):
        self.name = format_str

    def __str__(self):
        return '%s: Invalid format' % self.name


class InvalidEncodingError(VtkError):
    def __init__(self, encoding):
        self.name = encoding

    def __str__(self):
        return '%s: Invalid encoder' % self.name


def assemble_vtk_document(element):
    root = element['VTKFile']
    grid = element['Grid']
    piece = element['Piece']

    for section in _VTK_POSSIBLE_PIECE_SECTIONS:
        try:
            piece.appendChild(element[section])
        except (KeyError, EmptyElementError):
            pass
    grid.appendChild(piece)
    root.appendChild(grid)
  
    try:
        root.appendChild(element['AppendedData'])
    except KeyError:
        pass
  
    return root


def assert_format_is_valid(format_string):
    if format_string not in _VALID_FORMATS:
        raise InvalidFormatError(format_string)


def assert_encoding_is_valid(encoding_string):
    if encoding not in _VALID_ENCODINGS:
        raise InvalidEncodingError(encoding)
  
  
class VtkWriter(xml.dom.minidom.Document):
    def __init__(self, **kwds):
        self._format = kwds.pop('format', 'ascii')
        self._encoding = kwds.pop('encoding', 'ascii')

        assert_format_is_valid(self.format)
        assert_encoding_is_valid(self.encoding)

        if self.format == 'ascii':
            encoding = 'ascii'

        if self.format == 'appended':
            self._data = VtkAppendedDataElement('', encoding=self.encoding)
        else:
            self._data = None
  
        xml.dom.minidom.Document.__init__(self)

    @property
    def format(self):
        return self._format

    @property
    def encoding(self):
        return self._encoding

    @property
    def data(self):
        return self._data

    def construct_field_elements(self, field):
        raise NotImplementedError()

    def write(self, path, field):
        self.unlink()
        elements = self.construct_field_elements(field)

        if self.data is not None:
            elements['AppendedData'] = self.data

        self.appendChild(assemble_vtk_document(elements))
        self.to_xml(path)
  
    def to_xml(self, path):
        with open(path, 'w') as xml_file:
            xml_file.write(self.toprettyxml())


def assemble_vtk_elements(element):
    root = element['VTKFile']
    grid = element['Grid']
    piece = element['Piece']
    for section in _VTK_FILE_SECTIONS:
        try:
            piece.appendChild(element[section])
        except (KeyError, EmptyElementError):
            pass
    grid.appendChild(piece)
    root.appendChild(grid)

    try:
        root.appendChild(element['AppendedData'])
    except KeyError:
        pass

    return root


class VTKDatabase(VtkWriter):
    def write (self, path, **kwargs):
        (base, fname) = os.path.split(path)
        (root, ext) = os.path.splitext(fname)

        try:
            next_file = '%s_%04d%s' % (root, self._count, ext)
        except NameError:
            self._count = 0
            next_file = '%s_%04d%s' % (root, self._count, ext)

        VtkWriter.write(self, os.path.join (base, next_file), **kwargs)

        self._count += 1
