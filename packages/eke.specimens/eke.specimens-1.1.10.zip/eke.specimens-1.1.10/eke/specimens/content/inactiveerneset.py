# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Inactive ERNE Set: content implementation'''

from base import ERNESpecimenSet, ERNESpecimenSetSchema
from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import IInactiveERNESet
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from Products.DataGridField import DataGridField, DataGridWidget, Column, SelectColumn
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
from eke.specimens import STORAGE_VOCAB_NAME

def asInt(s):
    '''Yield the string ``s`` as an integer, but yield zero if ``s`` can't be interpreted as an integer.'''
    try:
        return int(s)
    except ValueError:
        return 0


InactiveERNESetSchema = ERNESpecimenSetSchema.copy() + atapi.Schema((
    atapi.StringField(
        'contactName',
        required=False,
        storage=atapi.AnnotationStorage(),
        searchable=True,
        widget=atapi.StringWidget(
            label=_(u'Contact Name'),
            description=_(u'Name of the person to contact in order to obtain specimens from this set'),
        ),
    ),
    atapi.ComputedField(
        'storageType',
        expression='context._computeStorageTypes()',
        searchable=True,
        widget=atapi.ComputedWidget(
            label=_(u'Storage Types'),
            description=_(u'The ways in which specimens in this set are stored.'),
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
    DataGridField(
        'specimensByStorageType',
        columns=('storageType', 'numParticipants'),
        allow_empty_rows=False,
        searchable=True,
        widget=DataGridWidget(
            label=_(u'Stored Specimens'),
            description=_(u'The number of participants by each storage type.'),
            columns={
                'storageType': SelectColumn(_(u'Storage Type'), 'getStorageTypeDisplayList'),
                'numParticipants': Column(_(u'Number Participants'), default=0),
            },
        ),
    ),
))

finalizeATCTSchema(InactiveERNESetSchema, folderish=True, moveDiscussion=True)

class InactiveERNESet(ERNESpecimenSet):
    '''A set of specimens from an inactive ERNE site.'''
    implements(IInactiveERNESet)
    portal_type   = 'Inactive ERNE Set'
    schema        = InactiveERNESetSchema
    contactName = atapi.ATFieldProperty('contactName')
    def getStorageTypeDisplayList(self):
        factory = getUtility(IVocabularyFactory, name=STORAGE_VOCAB_NAME)
        vocab = factory(self)
        return atapi.DisplayList([(i.token, i.title) for i in vocab])
    def _computeStorageTypes(self):
        field = self.getField('specimensByStorageType')
        return field.getColumn(self, 'storageType')
    def _computeNumParticipants(self):
        field = self.getField('specimensByStorageType')
        return sum([asInt(i) for i in field.getColumn(self, 'numParticipants')])


atapi.registerType(InactiveERNESet, PROJECTNAME)
