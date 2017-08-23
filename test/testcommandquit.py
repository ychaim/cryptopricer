import unittest
import os,sys,inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from commandquit import CommandQuit

class TestCommandQuit(unittest.TestCase):

    def testAbstractCommandInstanciation(self):
        self.fail("test not implemented")

if __name__ == '__main__':
    unittest.main()