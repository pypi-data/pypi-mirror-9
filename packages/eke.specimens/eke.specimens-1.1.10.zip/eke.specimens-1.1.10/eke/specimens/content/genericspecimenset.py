# encoding: utf-8
# Copyright 2010–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimen set: content implementation.'''

from base import SpecimenSetSchema, SpecimenSet
from eke.specimens import ProjectMessageFactory as _
from eke.specimens import STORAGE_VOCAB_NAME, COLLECTION_VOCAB_NAME
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import IGenericSpecimenSet, ICaseControlSubset
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

GenericSpecimenSetSchema = SpecimenSetSchema.copy() + atapi.Schema((
    atapi.StringField(
        'fullName',
        required=True,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Full Name'),
            description=_(u'Complete title for this specimen set.'),
            size=50,
        ),
    ),
    atapi.StringField(
        'contactName',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            title=_(u'Contact Name'),
            description=_(u'Optional name of a person to contact for information about this set.'),
        ),
    ),
    atapi.StringField(
        'contactEmail',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        validators=('isEmail',),
        widget=atapi.StringWidget(
            title=_(u'Contact Email'),
            description=_(u'Optional email address of a person to contact for information about this set.'),
        ),
    ),
    atapi.LinesField(
        'cancerLocations',
        required=False,
        storage=atapi.AnnotationStorage(),
        searchable=True,
        widget=atapi.LinesWidget(
            label=_(u'Cancer Locations'),
            description=_(u'List (one per line) of the locations where cancer was detected.'),
        ),
    ),
    atapi.LinesField(
        'storageType',
        required=False,
        multiValued=True,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=STORAGE_VOCAB_NAME,
        widget=atapi.MultiSelectionWidget( # TODO: Use InAndOutWidget
            label=_(u'Storage Types'),
            description=_(u'The ways specimens in this set are stored.'),
        ),
    ),
    atapi.LinesField(
        'collectionType',
        required=False,
        multiValued=True,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=COLLECTION_VOCAB_NAME,
        widget=atapi.MultiSelectionWidget(  # TODO: Use InAndOutWidget
            label=_(u'Collection Types'),
            description=_(u'What kinds of specimens were collected from participants'),
        ),
    ),
    atapi.BooleanField(
        'isPRoBE',
        required=False,
        default=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u'PRoBE'),
            description=_(u'Check the box is this is a PRoBE set, otherwise leave it unchecked.'),
        ),
    ),
    atapi.ComputedField(
        'numParticipants',
        expression='context._computeNumParticipants()',
        widget=atapi.ComputedWidget(
            label=_(u'Participants'),
            description=_(u'Total number of participants providing specimens in this set.'),
        ),
    ),
    atapi.ComputedField(
        'numCases',
        expression='context._computeNumCases()',
        widget=atapi.ComputedWidget(
            label=_(u'Cases'),
            description=_(u'Total number of cases.'),
        ),
    ),
    atapi.ComputedField(
        'numControls',
        expression='context._computeNumControls()',
        widget=atapi.ComputedWidget(
            label=_(u'Controls'),
            description=_(u'Total number of controls.'),
        ),
    ),
))


finalizeATCTSchema(GenericSpecimenSetSchema, folderish=True, moveDiscussion=False)

class GenericSpecimenSet(SpecimenSet):
    '''A generic set of specimens, such as for a reference set.'''
    implements(IGenericSpecimenSet)
    portal_type     = 'Generic Specimen Set'
    schema          = GenericSpecimenSetSchema
    cancerLocations = atapi.ATFieldProperty('cancerLocations')
    collectionType  = atapi.ATFieldProperty('collectionType')
    contactEmail    = atapi.ATFieldProperty('contactEmail')
    contactName     = atapi.ATFieldProperty('contactName')
    fullName        = atapi.ATFieldProperty('fullName')
    isPRoBE         = atapi.ATFieldProperty('isPRoBE')
    def _computeNumParticipants(self):
        factory = getToolByName(self, 'portal_factory')
        if factory.isTemporary(self): return 0
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(
            path=dict(query='/'.join(self.getPhysicalPath()), depth=1),
            object_provides=ICaseControlSubset.__identifier__
        )
        return sum([int(i.getNumParticipants) for i in brains])
    def _computeNumInSubset(self, kind):
        factory = getToolByName(self, 'portal_factory')
        if factory.isTemporary(self): return 0
        catalog = getToolByName(self, 'portal_catalog')
        brains = catalog(
            path=dict(query='/'.join(self.getPhysicalPath()), depth=1),
            object_provides=ICaseControlSubset.__identifier__,
            subsetType=kind
        )
        return sum([int(i.getNumParticipants) for i in brains])
    def _computeNumCases(self):
        return self._computeNumInSubset('Case')
    def _computeNumControls(self):
        return self._computeNumInSubset('Control')

atapi.registerType(GenericSpecimenSet, PROJECTNAME)
