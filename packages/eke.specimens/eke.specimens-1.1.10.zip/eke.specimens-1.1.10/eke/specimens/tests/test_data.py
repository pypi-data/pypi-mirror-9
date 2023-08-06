# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: test data files.
'''

import unittest2 as unittest
from eke.specimens import locateData
import os.path

class DataTest(unittest.TestCase):
    '''Unit tests data loading.'''
    def testLoadingData(self):
        '''Check if we can load our expected data files'''
        for fn in ('reference-sets', 'offline-site-specimen-summaries'):
            path = locateData(fn)
            self.failUnless(os.path.isfile(path), "Can't locate data file \"%s\"" % fn)
    def testLoadingNonexistentData(self):
        '''Ensure we can't load non-existent data files.'''
        path = locateData('non-existent-data-booga-booga')
        self.failIf(os.path.exists(path), "Was able to find a bogus data file")

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
