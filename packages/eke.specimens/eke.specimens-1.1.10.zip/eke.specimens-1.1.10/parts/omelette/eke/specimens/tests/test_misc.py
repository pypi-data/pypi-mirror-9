# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: miscellaneous tests.
'''

import unittest2 as unittest
from eke.specimens import safeInt
import os.path

class MiscTest(unittest.TestCase):
    '''Miscellaneous unit tests.'''
    def testSafeInt(self):
        '''Try out the safeInt function.'''
        self.assertEquals(1, safeInt('1'))
        self.assertEquals(0, safeInt('0'))
        self.assertEquals(0, safeInt('booga-booga'))
        self.assertEquals(0, safeInt(''))
        self.assertEquals(0, safeInt(None))

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
