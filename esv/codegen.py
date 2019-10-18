"""
The DataObjects module is a combination data parser and codegen tool.

In Python, it can be used to load structured data from files into
numpy recarrays, wrapped with useful indices, getters, and lookup
functions.

It can also produce classes for other languages to provide similar
functionality, given a source data file.

The data file should be in a fully-populated C{aura.file.esv}
format.
"""

from .schema import Schema
from mako.template import Template
import os

_TEMPLATE_PYCPP_FILE  = 'codegen.pycpp.mako'
_TEMPLATE_CPP_FILE    = 'codegen.cpp.mako'
_TEMPLATE_H_FILE      = 'codegen.hpp.mako'

_TYPE_MAP = {
    'S': 'std::string',
    'u': 'std::string',
    'i8': 'long',
    'i4': 'int',
    'i2': 'short',
    'i1': 'char',
    'f8': 'double',
    'f4': 'float',
    'int': 'int',
    'float': 'float',
}

def _get_ctype(np_type):
    if np_type[0] in '|<':
        np_type = np_type[1:]

    for a, b in _TYPE_MAP.items():
        if np_type.startswith(a):
            return b

    raise ValueError('Unable to determine C type for "%s"' % np_type)


def _full_path(filename):
    """
    Return the full path relative to this module.
    """
    return os.path.join(os.path.dirname(__file__), filename)

def _name_from_file(filename):
    """
    derive the class name from the filename.
    """
    basename = os.path.basename(filename).split('.')[0]
    return basename.lower().capitalize()


def _apply_template(content, schema, name, **kwargs):
    """
    Generic function to apply the given schema to a template,
    along with some additional keyword overrides.
    """
    # Convert the types to something C will understand.
    dtype = [(n, _get_ctype(t)) for n, t in schema.dtype]

    return Template(content).render(name=name,
                                    dtype=dtype,
                                    keys=schema.keys,
                                    indices=schema.indices,
                                    delimiter=schema.delimiter,
                                    null_string=schema.null_string,
                                    schema=schema,
                                    **kwargs)

def create_dataobj_h(esv_file_name, name=None):
    """
    Given the esv file, return the contents of the .h for the
    derived C++ implementation.
    """
    with open(esv_file_name) as infile:
        schema = Schema.parse(infile)

    with open(_full_path(_TEMPLATE_H_FILE)) as infile:
        content = infile.read()

    if name is None:
        name = _name_from_file(esv_file_name)

    return _apply_template(content, schema, name)

def create_dataobj_cpp(esv_file_name, name=None):
    """
    Given the esv file, return the contents of the .cpp for the
    derived C++ implementation.
    """
    with open(esv_file_name) as infile:
        schema = Schema.parse(infile)

    with open(_full_path(_TEMPLATE_CPP_FILE)) as infile:
        content = infile.read()

    if name is None:
        name = _name_from_file(esv_file_name)

    return _apply_template(content, schema, name)

def create_dataobj_pycpp(esv_file_name, name=None):
    """
    Given the esv file, return the contents of the .cpp for the
    derived C++ implementation.
    """
    with open(esv_file_name) as infile:
        schema = Schema.parse(infile)

    with open(_full_path(_TEMPLATE_PYCPP_FILE)) as infile:
        content = infile.read()

    if name is None:
        name = _name_from_file(esv_file_name)

    return _apply_template(content, schema, name)

