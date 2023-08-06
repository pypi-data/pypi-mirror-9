# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EDRN Knowledge Environment Specimens: views for content types.
'''

from Acquisition import aq_inner
from eke.specimens import STORAGE_VOCAB_NAME, ORGAN_VOCAB_NAME, COLLECTION_VOCAB_NAME, safeInt
from eke.specimens.interfaces import ISpecimenSystem, ISpecimenSet, ICaseControlSubset
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

def computeParticipants(brain):
    '''For some stupid reason, the "getNumParticipants" column gets hosed after a catalog rebuild, even
    though reindexing an individual specimen set re-populates the column just fine. WTF?'''
    value = safeInt(brain.getNumParticipants)
    if not value:
        # Is the value really zero?
        specimenSet = brain.getObject()
        actualValue = specimenSet.getNumParticipants()
        if actualValue == 0:
            # It really is zero. Wow.
            return 0
        # Ah ha. Reindex this individual specimen set so the "getNumParticipants" column gets fixed.
        specimenSet.reindexObject()
        return actualValue
    # Oh goodness gracious me, the column had a useful value!
    return value

def getStorageTypeLabel(storageType, context):
    if isinstance(storageType, basestring):
        storageType = (storageType,)
    labels = []
    for i in storageType:
        try:
            factory = getUtility(IVocabularyFactory, name=STORAGE_VOCAB_NAME)
            vocab = factory(context)
            labels.append(vocab.getTermByToken(i).title)
        except LookupError:
            labels.append(u'?')
    return u', '.join(labels)

def getOrganLabel(organID, context):
    if organID != 'unknown':
        try:
            factory = getUtility(IVocabularyFactory, name=ORGAN_VOCAB_NAME)
            vocab = factory(context)
            return vocab.getTermByToken(organID).title
        except LookupError:
            pass
    return u'?'

class SpecimenSystemFolderView(BrowserView):
    '''Default view of a Specimen System folder.'''
    __call__ = ViewPageTemplateFile('templates/specimensystemfolder.pt')
    def haveSpecimenSystems(self):
        return len(self.specimenSystems()) > 0
    @memoize
    def specimenSystems(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=ISpecimenSystem.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(
            title=i.Title, description=i.Description, numParticipants=computeParticipants(i), url=i.getURL()
        ) for i in results]
    def getStorageTypeLabel(self, storageType):
        context = aq_inner(self.context)
        return getStorageTypeLabel(storageType, context)


class SpecimenSystemView(BrowserView):
    '''Default view of a Specimen System.'''
    __call__ = ViewPageTemplateFile('templates/specimensystem.pt')
    def haveSpecimenSets(self):
        return len(self.specimenSets()) > 0
    @memoize
    def specimenSets(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=ISpecimenSet.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(
            title=i.Title,
            description=i.Description,
            numParticipants=computeParticipants(i),
            url=i.getURL()
        ) for i in results]

class ERNESpecimenSystemView(SpecimenSystemView):
    '''Default view of an ERNE Specimen System.'''
    __call__ = ViewPageTemplateFile('templates/ernespecimensystem.pt')
    

class GenericSpecimenSetView(BrowserView):
    '''Default view of a Generic Specimen Set.'''
    __call__ = ViewPageTemplateFile('templates/genericspecimenset.pt')
    def cases(self):
        return self.getSubsets('Case')
    def controls(self):
        return self.getSubsets('Control')
    def getCancerLocations(self):
        context = aq_inner(self.context)
        return u', '.join(context.cancerLocations)
    @memoize
    def getAbstract(self):
        abstract = None
        context = aq_inner(self.context)
        protocol = context.protocol
        if protocol is not None:
            abstract = protocol.abstract
            if not abstract:
                abstract = protocol.Description()
        return abstract
    @memoize
    def getSubsets(self, kind):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(
            object_provides=ICaseControlSubset.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            subsetType=kind,
            sort_on='sortable_title'
        )
        return [dict(title=i.Title, numParticipants=computeParticipants(i)) for i in brains]
    def getTotalParticipants(self, kind):
        return sum([int(i['numParticipants']) for i in self.getSubsets(kind)])
    def totalCases(self):
        return self.getTotalParticipants('Case')
    def totalControls(self):
        return self.getTotalParticipants('Control')
    def haveAttachedFiles(self):
        return len(self.attachedFiles()) > 0
    @memoize
    def attachedFiles(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(portal_type='File',path=dict(query='/'.join(context.getPhysicalPath()),depth=1),sort_on='sortable_title')
        return [dict(title=i.Title, description=i.Description, url=i.getURL()) for i in brains]
    def haveLinks(self):
        return len(self.links()) > 0
    @memoize
    def links(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        brains = catalog(portal_type='Link',path=dict(query='/'.join(context.getPhysicalPath()),depth=1),sort_on='sortable_title')
        return [dict(title=i.Title, description=i.Description, url=i.getURL()) for i in brains]
    @memoize
    def collectionTypes(self):
        context = aq_inner(self.context)
        vf = getUtility(IVocabularyFactory, name=COLLECTION_VOCAB_NAME)
        v = vf(context)
        captions = []
        for ident in context.collectionType:
            captions.append(v.getTerm(ident).title)
        captions.sort()
        return u', '.join(captions)
    @memoize
    def storageTypes(self):
        context = aq_inner(self.context)
        vf = getUtility(IVocabularyFactory, name=STORAGE_VOCAB_NAME)
        v = vf(context)
        captions = []
        for ident in context.getStorageType():
            captions.append(v.getTerm(ident).title)
        captions.sort()
        return u', '.join(captions)


class CaseControlSubsetView(BrowserView):
    '''Default view of a Case Control Subset.'''
    __call__ = ViewPageTemplateFile('templates/casecontrolsubset.pt')

class ERNESetView(BrowserView):
    '''Abstract ERNE view.'''
    def getOrgans(self):
        context = aq_inner(self.context)
        return u', '.join(context.organs)
    @memoize
    def collectionType(self):
        context = aq_inner(self.context)
        vf = getUtility(IVocabularyFactory, name=COLLECTION_VOCAB_NAME)
        v = vf(context)
        return v.getTerm(context.collectionType).title
    

class InactiveERNESetView(ERNESetView):
    '''Default view of an Inactive ERNE Set.'''
    __call__ = ViewPageTemplateFile('templates/inactiveerneset.pt')
    

class ActiveERNESetView(ERNESetView):
    '''Default view of an Active ERNE Set.'''
    __call__ = ViewPageTemplateFile('templates/activeerneset.pt')
    @memoize
    def storageType(self):
        context = aq_inner(self.context)
        vf = getUtility(IVocabularyFactory, name=STORAGE_VOCAB_NAME)
        v = vf(context)
        return v.getTerm(context.getStorageType()).title
    

