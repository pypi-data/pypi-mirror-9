# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: test the setup of this package.
'''

import unittest2 as unittest
from eke.specimens.testing import EKE_SPECIMENS_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from eke.specimens import STORAGE_VOCAB_NAME, ORGAN_VOCAB_NAME, COLLECTION_VOCAB_NAME

class SetupTest(unittest.TestCase):
    '''Unit tests the setup of this package.'''
    layer = EKE_SPECIMENS_INTEGRATION_TESTING
    def setUp(self):
        super(SetupTest, self).setUp()
        self.portal = self.layer['portal']
    def testTypes(self):
        '''Make sure our types are available.'''
        types = getToolByName(self.portal, 'portal_types').objectIds()
        for i in (
            'Case Control Subset',
            'Generic Specimen Set',
            'Inactive ERNE Set',
            'Specimen System Folder',
            'Specimen System',
        ):
            self.failUnless(i in types)
    def testCatalogIndexes(self):
        '''Check if indexes are properly installed.'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes = catalog.indexes()
        for i in (
            'getStorageType',
            'subsetType',
            'getNumParticipants',
            'getSystemName',
            'diagnosis',
            'collectionType',
            'siteName',
        ):
            self.failUnless(i in indexes, 'Index "%s" not in catalog' % i)
    def testCatalogMetadata(self):
        '''Check if indexed metadata schema are properly installed.'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        metadata = catalog.schema()
        for i in ('getStorageType', 'getNumParticipants', 'getSystemName', 'siteName'):
            self.failUnless(i in metadata)
    def testAddons(self):
        '''Check that dependent packages are installed'''
        qi = getToolByName(self.portal, 'portal_quickinstaller')
        # TODO: When we migrate from Archetypes to Dexterity, check for plone.app.dexterity
        # self.failUnless(qi.isProductInstalled('plone.app.dexterity'), "Dexterity wasn't installed")
    def testVocabularies(self):
        '''Ensure our vocabularies are available'''
        vocabs = (
            STORAGE_VOCAB_NAME, ORGAN_VOCAB_NAME, COLLECTION_VOCAB_NAME
        )
        for v in vocabs:
            self.failUnless(queryUtility(IVocabularyFactory, name=v) is not None, 'Vocabulary "%s" not available' % v)
    def testStorageVocabulary(self):
        '''Ensure the storage vocab has the "missing" storage terms'''
        factory = queryUtility(IVocabularyFactory, name=STORAGE_VOCAB_NAME)
        vocab = factory(self.portal)
        for ident, caption in (
            (u'28', u'Cyst aspirate'),
            (u'29', u'Blood spot card'),
            (u'31', u'EDTA plasma'),
            (u'32', u'Citrate plasma'),
            (u'33', u'EDTA cellular fraction'),
            (u'34', u'Citrate cellular fraction'),
            (u'40', u'DNA from blood'),
            (u'41', u'DNA from buccal cells'),
            (u'42', u'Tissue slides'),
            (u'45', u'Cell line'),
            (u'50', u'Buccal cells'),
            (u'51', u'Buffy coat'),
            (u'52', u'DNA from buffy coat'),
            (u'53', u'DNA from Lymphoblastoid cell lines'),
            (u'54', u'DNA from tumor tissue, paraffin block'),
            (u'55', u'Peripheral blood mononuclear cells (PBMC)'),
            (u'56', u'Saliva'),
            (u'57', u'Tumor tissue, paraffin block'),
            (u'58', u'Tumor tissue, slide'),
            (u'59', u'Induced sputum'),
            (u'60', u'Spontaneous sputum'),
            (u'61', u'Urine, pellet'),
            (u'62', u'Urine, soluble'),
            (u'63', u'Urine, cellular material'),
            (u'64', u'Semen'),
            (u'95', u'Other'),
            (u'97', u'Other, specify:'),
        ):
            term = vocab.getTerm(ident)
            self.assertEquals(caption, term.title)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
