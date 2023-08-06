# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: content base implementations and common features.'''

from Acquisition import aq_inner, aq_parent
from eke.specimens import ProjectMessageFactory as _
from Products.Archetypes import atapi
from zope.schema.interfaces import IVocabularyFactory
from eke.specimens.interfaces import ISpecimenSet, IERNESpecimenSet
from zope.schema.vocabulary import SimpleVocabulary
from zope.interface import directlyProvides
from Products.CMFCore.utils import getToolByName
from eke.specimens import STORAGE_VOCAB_NAME, COLLECTION_VOCAB_NAME
from Products.ATContentTypes.content import folder
from zope.interface import implements

# FIXME: not i18n
_diagnoses = SimpleVocabulary.fromItems((
    ('With Cancer', 'With Cancer'),
    ('Without Cancer', 'Without Cancer'),
))

TextuallyEnhancedSchema = atapi.Schema(( # Corresponds to eke.specimens.interfaces.ITextuallyEnhanced
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
            description=_(u'Additional richly-formatted text to display.'),
            rows=10,
            allow_file_upload=False,
        ),
    ),
))
SpecimenSetSchema = folder.ATFolderSchema.copy() + TextuallyEnhancedSchema.copy() + atapi.Schema((
    atapi.ReferenceField(
        'protocol',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=False,
        vocabulary_factory=u'eke.study.ProtocolsVocabulary',
        relationship='protocolProvidingSpecimens',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Protocol'),
            description=_(u'The single protocol that guided collection of specimens in this set'),
        ),
    ),
    atapi.ComputedField(
        'systemName',
        expression='context._computeSystemName()',
        searchable=True,
        widget=atapi.ComputedWidget(
            label=_(u'System'),
            description=_(u'To what system this specimen set belongs.'),
        ),
    ),
))
SpecimenSetSchema['title'].widget.label = _(u'Short Name')
SpecimenSetSchema['title'].widget.description = _(u'Enter a short, unique identifier for this specimen set.')
SpecimenSetSchema['title'].storage = atapi.AnnotationStorage()
SpecimenSetSchema['description'].storage = atapi.AnnotationStorage()

class SpecimenSet(folder.ATFolder):
    '''Abstract set of specimens.  This is a base class.'''
    implements(ISpecimenSet)
    schema      = SpecimenSetSchema
    title       = atapi.ATFieldProperty('title')
    description = atapi.ATFieldProperty('description')
    protocol    = atapi.ATReferenceFieldProperty('protocol')
    text        = atapi.ATFieldProperty('text')
    def _computeSystemName(self):
        factory = getToolByName(self, 'portal_factory')
        if factory.isTemporary(self): return u''
        parent = aq_parent(aq_inner(self))
        return parent.title


def specimenSystemNamesVocabularyFactory(context):
    catalog = getToolByName(context, 'portal_catalog')
    items = list(catalog.uniqueValuesFor('getSystemName'))
    items.sort()
    return SimpleVocabulary.fromItems([(i.decode('utf-8'), i.decode('utf-8')) for i in items])
directlyProvides(specimenSystemNamesVocabularyFactory, IVocabularyFactory)

def diagnosesVocabularyFactory(context):
    return _diagnoses
directlyProvides(diagnosesVocabularyFactory, IVocabularyFactory)

def sitesWithSpecimensVocabulary(context):
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog(object_provides=IERNESpecimenSet.__identifier__)
    class _Site(object):
        def __init__(self, uid, name):
            self.uid, self.name = uid, name
        def __cmp__(self, other):
            return cmp(self.name, other.name)
    sites = frozenset([_Site(i.UID, i.siteName.decode('utf-8')) for i in results])
    sites = list(sites)    
    sites.sort()
    return SimpleVocabulary([SimpleVocabulary.createTerm(i.uid, i.uid, i.name) for i in sites])    
directlyProvides(sitesWithSpecimensVocabulary, IVocabularyFactory)

ERNESpecimenSetSchema = SpecimenSetSchema.copy() + atapi.Schema((
    atapi.ReferenceField(
        'site',
        required=False,
        searchable=False,
        multiValued=False,
        storage=atapi.AnnotationStorage(),
        relationship='siteWhereTheseSpecimensAreCurated',
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.site.Sites',
        widget=atapi.ReferenceWidget(
            label=_(u'Site'),
            description=_(u'Site housing these specimens.'),
        ),
    ),
    atapi.ComputedField(
        'siteName',
        expression='context._computeSiteName()',
        searchable=True,
        widget=atapi.ComputedWidget(
            label=_(u'Site Name'),
            description=_(u'At what site are these specimens curated.'),
        ),
    ),
    atapi.LinesField(
        'organs',
        required=False,
        storage=atapi.AnnotationStorage(),
        searchable=True,
        widget=atapi.LinesWidget(
            label=_(u'Organs'),
            description=_(u'List (one per line) of the organs from which specimens were collected.'),
        ),
    ),
    atapi.StringField(
        'collectionType',
        required=False,
        multiValued=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=COLLECTION_VOCAB_NAME,
        widget=atapi.SelectionWidget(
            label=_(u'Collection Type'),
            description=_(u'What kind of specimen was collected from participants.'),
        ),
    ),
))

class ERNESpecimenSet(SpecimenSet):
    '''An abstract set of ERNE specimens.'''
    implements(IERNESpecimenSet)
    schema         = ERNESpecimenSetSchema
    site           = atapi.ATReferenceFieldProperty('site')
    organs         = atapi.ATFieldProperty('organs')
    collectionType = atapi.ATFieldProperty('collectionType')
    siteName       = atapi.ATFieldProperty('siteName')
    def _computeSiteName(self):
        return self.site.title if self.site is not None else u''

