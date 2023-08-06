# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: test the ingest of specimen data.
'''

import unittest2 as unittest
from eke.specimens.testing import EKE_SPECIMENS_FIXTURE
from eke.specimens.browser.utils import getSpecimens, ERNESpecimenSummary

class SpecimenSummaryTest(unittest.TestCase):
    '''Tests of the SpecimenSummary class'''
    def testComparisons(self):
        a0 = ERNESpecimenSummary('3', 123, 10, 5, '16', True, True, 'x@y.com', 116, 15)
        a1 = ERNESpecimenSummary('3', 123, 10, 5, '16', True, True, 'x@y.com', 116, 15)
        b  = ERNESpecimenSummary('3', 123, 10, 5, '16', True, True, 'w@y.com', 116, 15)
        c  = ERNESpecimenSummary('3', 123, 10, 5, '16', True, True, 'z@x.com', 116, 15)
        d  = ERNESpecimenSummary('2', 123, 10, 5, '16', True, True, 'x@y.com', 116, 15)
        e  = ERNESpecimenSummary('3', 123, 10, 6, '16', True, True, 'x@y.com', 116, 15)
        f  = ERNESpecimenSummary('3', 124, 10, 5, '16', True, True, 'x@y.com', 116, 15)
        self.assertEquals(a0, a0)
        self.assertEquals(a0, a1)
        self.failUnless(a0 != b)
        self.failUnless(a0 <= a1)
        self.failUnless(a0 >= b)
        self.failUnless(a0 > b)
        self.failUnless(a0 <= c)
        self.failUnless(a0 < c)
        self.failUnless(a0 >= d)
        self.failUnless(a0 > d)
        self.failUnless(d < b < a0)
        self.failUnless(a0 < e)
        self.failUnless(a0 < f)
    def testHashability(self):
        a0 = ERNESpecimenSummary('3', 123, 10, 5, '16', True, True, 'x@y.com', 116, 15)
        a1 = ERNESpecimenSummary('3', 123, 10, 5, '16', True, True, 'x@y.com', 116, 15)
        b  = ERNESpecimenSummary('3', 123, 10, 5, '16', True, True, 'x@z.com', 116, 15)
        self.assertEquals(hash(a0), hash(a1))
        self.failUnless(hash(a0) != hash(b))

class IngestTest(unittest.TestCase):
    '''Unit tests of ingestion.'''
    layer = EKE_SPECIMENS_FIXTURE
    def testNormalSpecimens(self):
        '''Check if ``getSpecimens`` returns reasonable results on test data'''
        records = getSpecimens('testscheme://localhost/erne/prod', 'testscheme://localhost/erne/erneQuery')
        records.sort()
        self.assertEquals(3, len(records))
        self.assertEquals(ERNESpecimenSummary('5', 1, 1, 0, '16', False, True, 'z@y.com', '116', '15'), records[0])
        self.assertEquals(ERNESpecimenSummary('5', 1, 1, 0, '16', True, True, 'z@y.com', '116', '15'), records[1])
        self.assertEquals(ERNESpecimenSummary('6', 1, 1, 0, '16', True, True, 'z@y.com', '116', '15'), records[2])

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
