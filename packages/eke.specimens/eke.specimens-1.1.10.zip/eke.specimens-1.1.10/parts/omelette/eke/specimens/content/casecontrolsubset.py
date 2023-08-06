# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: case/control subset content implementation.'''

from eke.specimens.config import PROJECTNAME
from eke.specimens import ProjectMessageFactory as _
from Products.Archetypes import atapi
from zope.schema.interfaces import IVocabularyFactory
from eke.specimens.interfaces import ICaseControlSubset
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import directlyProvides
from Products.ATContentTypes.content import schemata, base
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements

_subsetTypes = SimpleVocabulary.fromItems((
    ('Case', 'Case'),
    ('Control', 'Control'),
))

CaseControlSubsetSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((
    atapi.StringField(
        'subsetType',
        enforceVocabulary=True,
        required=True,
        default='Case',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.specimens.vocab.SubsetType',
        storage=atapi.AnnotationStorage(),
        widget=atapi.SelectionWidget(
            label=_(u'Subset Type'),
            description=_(u'Are participants in this subset positive (case) or negative (control)?')
        ),
    ),
    atapi.IntegerField(
        'numParticipants',
        required=True,
        default=0,
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u'Participants'),
            description=_(u'How many participants were in this subset.'),
        ),
    ),
))

CaseControlSubsetSchema['title'].storage = atapi.AnnotationStorage()
CaseControlSubsetSchema['title'].widget.description = _(u'The name of this case/control subset.')
CaseControlSubsetSchema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(CaseControlSubsetSchema, folderish=False, moveDiscussion=True)

class CaseControlSubset(base.ATCTContent):
    '''A subset of either case or control participants.'''
    implements(ICaseControlSubset)
    portal_type = 'Case Control Subset'
    schema = CaseControlSubsetSchema
    title = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    subsetType = atapi.ATFieldProperty('subsetType')

atapi.registerType(CaseControlSubset, PROJECTNAME)

def subsetTypeVocabularyFactory(context):
    return _subsetTypes
directlyProvides(subsetTypeVocabularyFactory, IVocabularyFactory)
