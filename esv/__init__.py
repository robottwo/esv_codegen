"""
This module is for reading and writing enhanced csv files. These
are ascii-based, delimitted data files with additional header information.

This module is for working with generic esv files in Python.
"""
UNICODE = 'utf-8'
import numpy as np
import types
from .schema import Schema

class ESV(object):
    """
    A DataObject collection. This structure is roughly a numpy recarray
    with additional lookup methods provided for convenience.
    """
    CONVERSION_MAP = { '|S': str,
                       '|u': lambda x: x if isinstance(x, unicode) else unicode(x, UNICODE) if isinstance(x, str) else str(x).decode(UNICODE),
                       '<i8': int,
                       '<f8': float}

    def __repr__(self):
        return 'ESV(%d rows, %s)' % (self._data.size, self._schema.dtype)

    def __str__(self):
        return self.to_string()

    def mask(self, slice_or_mask):
        """
        Return a new DObject, with the slice_or_mask applied to the recarray.
        """
        o = self.__class__()
        o._schema = self._schema
        o._data = self._data[slice_or_mask]
        o.reindex()
        return o

    def dump(self, file_obj):
        file_obj.write(self._schema.to_string())
        np.savetxt(file_obj,
                   self._data,
                   delimiter=self._schema.delimiter,
                   fmt=['%s' for e in self._schema.dtype],)

    def dump_file(self, filename):
        with open(filename, 'w') as outfile:
            self.dump(outfile)

    def to_string(self):
        from cStringIO import StringIO
        stream = StringIO()
        self.dump(stream)
        return stream.getvalue()

    def _get_converters(self):
      """
      Returns a dict of columns to converter functions.
      """
      converters = {}
      for field, ftype in self._schema.dtype:
          if isinstance(ftype, str):
              for s, t in self.CONVERSION_MAP.items():
                  if ftype.startswith(s):
                      converters[field] = t
          else:
              converters[field] = ftype

      return converters

    @classmethod
    def from_recarray(cls, recarray):
        o = cls()
        o._data = recarray
        o._schema = Schema()
        o._schema.dtype = o._data.dtype.descr
        return o

    @classmethod
    def load_file(cls, filename, header=None):
        with open(filename, 'r') as infile:
            return cls.load(infile, header)

    @classmethod
    def load(cls, file_obj, header=None):
        """
        Load this class from a file.
        """
        o = cls()
        if header is None:
            o._schema = Schema.parse(file_obj)
        else:
            o._schema = Schema.parse_string(header)
        file_obj.seek(0)
        if o._schema.delimiter == ' ':
            o._data = np.genfromtxt(file_obj,
                                    dtype=o._schema.dtype,
                                    names=[d[0] for d in o._schema.dtype],
                                    comments='#',
                                    skip_header=o._schema.header_lines,
                                    converters=o._get_converters(),
                                    missing_values=o._schema.null_string,
                                    )
        else:
            o._data = np.genfromtxt(file_obj,
                                    dtype=o._schema.dtype,
                                    names=[d[0] for d in o._schema.dtype],
                                    comments='#',
                                    delimiter=o._schema.delimiter,
                                    converters=o._get_converters(),
                                    missing_values=o._schema.null_string,
                                    )
        o.reindex()
        return o

    def reindex(self):
        # Build the key lookup table
        self._indices = {}
        for key_name in np.unique(self._schema.keys + self._schema.indices):
            self._indices[key_name] = {}
            keys= np.unique(self._data[key_name])
            for key in keys:
                lookup = np.where(self._data[key_name] == key)
                self._indices[key_name][key] = lookup

            if key_name in self._schema.keys:
                if np.unique(self._data[key_name]).size != self._data.size:
                    raise ValueError('%s has non-unique keys!' % key_name)

                func_name = 'get_by'
                def get(self, k, __key_name=key_name):
                    return self._data[self._indices[__key_name][k]][0]
                get.__doc__ = "Retrieve one entry by %s" % key_name
            else:
                func_name = 'search'
                def get(self, k, __key_name=key_name):
                    return self._data[self._indices[__key_name][k]]
                get.__doc__ = "Retrieve entries by %s" % key_name

            # Add the lookup method
            get = types.MethodType(get, self)
            self.__setattr__('%s_%s' % (func_name, key_name), get)


    @classmethod
    def load_string(cls, string, header=None):
        from cStringIO import StringIO
        stream = StringIO(string)
        return cls.load(stream, header)

    def __len__(self):
      return len(self._data)

    @property
    def recarray(self):
        return self._data

def load_recarray(filename):
    """
    Load an ESV file directly into a recarray.
    """
    return ESV.load_file(filename).recarray

def dump_recarray(filename, recarray):
    """
    Dumpy a recarray to an ESV file.
    """
    ESV.from_recarray(recarray).dump_file(filename)