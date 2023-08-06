# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Inactive ERNE Set: content implementation'''

from base import ERNESpecimenSet, ERNESpecimenSetSchema
from eke.specimens import ProjectMessageFactory as _
from eke.specimens import STORAGE_VOCAB_NAME, safeInt
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import IActiveERNESet
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements

ActiveERNESetSchema = ERNESpecimenSetSchema.copy() + atapi.Schema((
    atapi.StringField(
        'storageType',
        required=False,
        storage=atapi.AnnotationStorage(),
        multiValued=False,
        enforceVocabulary=True,
        vocabulary_display_path_bound=-1,
        vocabulary_factory=STORAGE_VOCAB_NAME,
        searchable=True,
        widget=atapi.SelectionWidget(
            label=_(u'Storage Type'),
            description=_(u'How these specimens were stored.'),
        ),
    ),
    atapi.IntegerField(
        'numCases',
        required=False,
        default=0,
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u'Cases'),
            description=_(u'How many cancer-positive cases provided specimens.'),
        ),
    ),
    atapi.IntegerField(
        'numControls',
        required=False,
        default=0,
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u'Controls'),
            description=_(u'How many cancer-negative controls provided specimens.'),
        ),
    ),
    atapi.StringField(
        'diagnosis',
        required=True,
        default='With Cancer',
        multiValued=False,
        enforceVocabulary=True,
        vocabulary_factory=u'eke.specimens.vocab.Diagnoses',
        vocabulary_display_path_bound=-1,
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u'Cancer Diagnosis'),
            description=_(u'Either with cancer, or not.'),
        ),
    ),
    atapi.ComputedField(
        'numParticipants',
        expression='context._computeNumParticipants()',
        widget=atapi.ComputedWidget(
            label=_(u'Participants'),
            description=_(u'Total number of participants providing specimens.'),
        ),
    ),
))

finalizeATCTSchema(ActiveERNESetSchema, folderish=True, moveDiscussion=True)

class ActiveERNESet(ERNESpecimenSet):
    '''A set of specimens from an active ERNE site.'''
    implements(IActiveERNESet)
    portal_type = 'Active ERNE Set'
    schema      = ActiveERNESetSchema
    numCases    = atapi.ATFieldProperty('numCases')
    numControls = atapi.ATFieldProperty('numControls')
    diagnosis   = atapi.ATFieldProperty('diagnosis')
    def _computeNumParticipants(self):
        return safeInt(self.numCases) + safeInt(self.numControls)

atapi.registerType(ActiveERNESet, PROJECTNAME)
