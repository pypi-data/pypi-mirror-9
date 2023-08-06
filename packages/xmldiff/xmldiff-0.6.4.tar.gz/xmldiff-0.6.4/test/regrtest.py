"""
xmldiff non regression test
"""
__revision__ = "$Id: regrtest.py,v 1.6 2003/10/02 10:56:18 syt Exp $"

from logilab.xmldiff import xmldiff
from os.path import join, basename
from cStringIO import StringIO
import sys
import unittest
import glob

DATA_DIR = 'data'
class BaseTest(unittest.TestCase):
    def check_output(self, options, expected):
        # redirect output
        output = StringIO()
        stdout = sys.stdout
        sys.stdout = output            
        try:
            try:
                xmldiff.run('xmldiff', *options)
            except SystemExit:
                pass
        finally:                
            sys.stdout = stdout
        data = output.getvalue().strip()
        self.assertEqual(data, expected, '%s:\n%r != %r' %
                         (self.name, data, expected) )
        

class DiffTest(BaseTest):
    
    def test(self):
        old = self.data['old']
        new = self.data['new']
        for options, res_file in self.data['result']:
            options = options + [old, new]
            f = open(res_file)
            expected = f.read().strip()
            self.check_output(options, expected)


class RecursiveDiffTest(BaseTest):
    name = 'RecursiveDiffTest'
    def test(self):
        options = ['-r', join(DATA_DIR, 'dir1'), join(DATA_DIR, 'dir2')]
        expected = """--------------------------------------------------------------------------------
FILE: onlyindir1.xml deleted
--------------------------------------------------------------------------------
FILE: onlyindir2.xml added
--------------------------------------------------------------------------------
FILE: inbothdir.xml"""
        self.check_output(options, expected)

        
def make_tests():
    """generate tests classes from test info
    
    return the list of generated test classes
    """
    tests_files = glob.glob(join(DATA_DIR, '*.xml')) + glob.glob(join(DATA_DIR, '*_result'))
    tests = {}
    # regroup test files
    for file in tests_files:
        base = basename(file)
        name = base[:6]
        type = base[7:]
        if type == '1.xml':
            tests.setdefault(name, {})['old'] = file
        elif type == '2.xml':
            tests.setdefault(name, {})['new'] = file
        else:
            options = type.split('_')[1:]
            tests.setdefault(name, {}).setdefault('result', []).append(
                [options, file])
            
    result = []
    for test_name, test_dict in tests.items():
        try:
            old = test_dict['old']
            new = test_dict['new']
            res_data = test_dict['result']
        except KeyError, e:
            msg = '** missing files in %s (%s)' % (test_name, e)
            print >>sys.stderr, msg
            continue
            
        class DiffTestSubclass(DiffTest):
            name = test_name
            data = test_dict
                
        result.append(DiffTestSubclass)
    return result


    
def suite():
    return unittest.TestSuite([unittest.makeSuite(test)
                               for test in make_tests() + [RecursiveDiffTest]])

def Run(runner=None):
    testsuite = suite()
    if runner is None:
        runner = unittest.TextTestRunner()
    return runner.run(testsuite)

   
if __name__ == '__main__':
    Run()
