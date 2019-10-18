"""
Codegen test module.
"""

import os, sys, tempfile, unittest
from .. import codegen

def _locate(filename):
    """
    Find the file relative to where the test is located.
    """
    return os.path.join(os.path.dirname(__file__), filename)


class CPP_T(unittest.TestCase):
    """
    Class for testing CPP codegen.
    """
    def t_valid1(self):
        self.check_valid('valid1')

    def t_valid2(self):
        self.check_valid('valid2')

    def check_valid(self, basename):
        """
        Generate the code for valid1, compile a test program, and run it.
        """
        esvfile = _locate(basename + '.esv')
        test_cpp_file = _locate(basename + '_test.cpp')
        hpp_source = codegen.create_dataobj_h(esvfile)
        cpp_source = codegen.create_dataobj_cpp(esvfile)

        temp_dir = os.path.join(tempfile.gettempdir(),
                                str(os.getpid()))
        os.makedirs(temp_dir)
        header_file = os.path.join(temp_dir, basename + '.hpp')
        source_file = os.path.join(temp_dir, basename + '.cpp')

        for filename, source in ((header_file, hpp_source),
                                 (source_file, cpp_source)):
            with open(filename, 'w') as outfile:
                outfile.write(source)

        test_prog = os.path.join(temp_dir, 'testprog')
	cmd = ('g++ -g -I %s -Wall %s %s -o %s\n' %
               (temp_dir, source_file, test_cpp_file, test_prog))
        sys.stderr.write(cmd)
        self.assertFalse(os.system(cmd))

        self.assertFalse(os.system(test_prog))
        os.unlink(header_file)
        os.unlink(source_file)
        os.unlink(test_prog)
        os.rmdir(temp_dir)
