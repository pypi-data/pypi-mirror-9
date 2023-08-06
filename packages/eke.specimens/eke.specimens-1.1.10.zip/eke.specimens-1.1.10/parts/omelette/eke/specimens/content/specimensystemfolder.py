# encoding: utf-8
# Copyright 2010–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Specimen system folder: content implementation.'''

from eea.facetednavigation.interfaces import IPossibleFacetedNavigable
from eke.specimens import ProjectMessageFactory as _
from eke.specimens.config import PROJECTNAME
from eke.specimens.interfaces import ISpecimenSystemFolder
from eke.specimens.utils import setFacetedNavigation
from Products.Archetypes import atapi
from Products.ATContentTypes.content import folder
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

SpecimenSystemFolderSchema = folder.ATFolderSchema.copy() + atapi.Schema((
    atapi.TextField(
        'text',
        required=False,
        searchable=True,
        primary=True,
        storage=atapi.AnnotationStorage(),
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(u'Body Text'),
            description=_(u'Full body text to display on this folder above its contents.'),
            rows=10,
            allow_file_upload=False,
        ),
    ),
))
SpecimenSystemFolderSchema['title'].storage = atapi.AnnotationStorage()
SpecimenSystemFolderSchema['description'].storage = atapi.AnnotationStorage()

finalizeATCTSchema(SpecimenSystemFolderSchema, folderish=True, moveDiscussion=False)

class SpecimenSystemFolder(folder.ATFolder):
    '''Specimen system folder which contains specimen system.'''
    implements(ISpecimenSystemFolder, IPossibleFacetedNavigable)
    portal_type       = 'Specimen System Folder'
    schema            = SpecimenSystemFolderSchema
    title             = atapi.ATFieldProperty('title')
    description       = atapi.ATFieldProperty('description')
    text              = atapi.ATFieldProperty('text')
    

atapi.registerType(SpecimenSystemFolder, PROJECTNAME)

def addFacetedNavigation(obj, event):
    '''Set up faceted navigation on all newly created Specimen System Folders.'''
    if not ISpecimenSystemFolder.providedBy(obj): return
    factory = getToolByName(obj, 'portal_factory')
    if factory.isTemporary(obj): return
    request = obj.REQUEST
    setFacetedNavigation(obj, request)
