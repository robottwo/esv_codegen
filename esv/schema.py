"""
Module for representing and parsing an ESV schema. Schemas can be
represented in text files with the following syntax:

#@esv field1 field2 field3
#
# The file begins with a special #@esv string.
# These comment lines are ignored.

# Field types are designated as follows:
#@field <field> <type> [index|key]
#
# <type> follows numpy conventions.
#
# The 'index' keyword means that the field can be used as a hash lookup,
# and the key does not need to be unique. A lookup will return a list of
# values.
#
# The 'key' keyword means that the field can be used as a hash lookup,
# and the key is unique. A lookup will result in only one value.

# A special string to represent null values:
#@null NULL

# Specify the delimiter. Defaults to whitespace.
#@delimiter \t
"""

import cStringIO

class Schema(object):
    """
    Represents an ESV schema.
    """
    __slots__ = [ 'null_string', 'dtype',
                  'keys', 'indices',
                  'delimiter', 'header_lines']

    def __repr__(self):
        """
        String representation.
        """
        return 'Schema(' + str(self.dtype) + ')'

    def __init__(self):
        self.keys = []
        self.indices = []
        self.null_string = 'null'
        self.delimiter = ' '

    @classmethod
    def parse_string(cls, string_data):
        """
        Parse a given the header information from a string.
        """
        string_io = cStringIO.StringIO(string_data)
        return cls.parse(string_io)


    @classmethod
    def parse(cls, fileobj):
        """
        Parse the header information from the fileobj.
        Stop parsing on the first non-blank, non-comment line.
        """
        o = cls()
        line_number = 0
        columns = []
        column_types = {}
        for line in fileobj.readlines():
            line = line.strip()
            line_number += 1
            if line_number == 1:
                if not line.startswith('#@esv'):
                    raise ValueError('Expected "#@esv," not "%s"' % line)
                else:
                    columns = line.split()[1:]
                continue

            if line.startswith("#@"):
                if line.startswith("#@field"):
                    field, col, ctype = line.split()[:3]
                    keywords = line.split()[3:]

                    if col not in columns:
                        raise ValueError("Unknown field: '%s' on line %d"
                                         % (col, line_number-1))
                    else:
                        column_types[col] = ctype.strip()

                    if 'key' in keywords:
                        o.keys.append(col)
                        keywords = [k for k in keywords if k != 'key']
                    if 'index' in keywords:
                        o.indices.append(col)
                        keywords = [k for k in keywords if k != 'index']
                    if len(keywords) > 0:
                        raise ValueError('Invalid Keywords %s on line %d'
                                         % (keywords, line_number-1))
                    continue

                if line.startswith('#@delimiter'):
                    o.delimiter = line[len('#@delimiter '):]
                    if o.delimiter == '':
                        o.delimiter = ' '
                    continue

                if line.startswith('#@null'):
                    o.null_string = line[len('#@null '):]
                    if o.null_string == '':
                        o.null_string = 'null'
                    continue

                if line.startswith("#@unique"):
                    # XXX: TODO: Implement unique multikeys.
                    continue

                raise ValueError('Unable to parse line %d: "%s"'
                                 % (line_number-1, line))
            elif line.startswith("#") or len(line) == 0:
                pass
            else:
                break
        o.header_lines = line_number - 1
        # Safety check to make sure we defined everything.
        for col in columns:
            if col not in column_types:
                raise ValueError('Missing #@field definition for "%s"' % col)
        o.dtype = [(col, column_types[col]) for col in columns]

        return o

    def to_string(self):
        """
        Dump the header to a string.
        """
        fields = [name for name,ntype in self.dtype]
        lines = ['#@esv ' + ' '.join(fields)]
        lines.append("#")
        for field, ftype in self.dtype:
            line = '#@field %s %s' % (field, ftype)
            if field in self.keys:
                line += ' key'
            elif field in self.indices:
                line += ' index'
            lines.append(line)
        lines.append("#")
        lines.append('#@delimiter %s' % self.delimiter)
        lines.append('#@null %s' % self.null_string)
        lines.append("#\n")
        return '\n'.join(lines)
