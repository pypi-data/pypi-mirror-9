# encoding: utf-8
# Copyright 2011–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eea.facetednavigation.settings.interfaces import IHidePloneRightColumn
from eke.specimens import STORAGE_VOCAB_NAME, COLLECTION_VOCAB_NAME
from eke.specimens.interfaces import ISpecimenSet
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.Portal import PloneSite
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

def setFacetedNavigation(folder, request):
    subtyper = getMultiAdapter((folder, request), name=u'faceted_subtyper')
    if subtyper.is_faceted or not subtyper.can_enable: return
    subtyper.enable()
    urlTool = getToolByName(folder, 'portal_url')
    path = '/' + '/'.join(urlTool.getRelativeContentPath(folder))
    criteria = ICriteria(folder)
    for cid in criteria.keys():
        criteria.delete(cid)
    criteria.add('resultsperpage', 'bottom', 'default', title='Results per page', hidden=True, start=0, end=50, step=5, default=20)
    criteria.add('sorting', 'bottom', 'default', title='Sort on', hidden=True, default='sortable_title')
    criteria.add(
        'checkbox', 'left', 'default',
        title='System',
        hidden=False,
        index='getSystemName',
        operator='or',
        vocabulary=u'eke.specimens.vocab.SystemNames',
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False,
    )
    criteria.add(
        'checkbox', 'left', 'default',
        title='Diagnosis',
        hidden=False,
        index='diagnosis',
        operator='or',
        vocabulary=u'eke.specimens.vocab.Diagnoses',
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False,
    )
    criteria.add(
        'checkbox', 'left', 'default',
        title='Storage',
        hidden=False,
        index='getStorageType',
        operator='or',
        vocabulary=STORAGE_VOCAB_NAME,
        count=False,
        maxitems=5,
        sortreversed=False,
        hidezerocount=False,
    )
    criteria.add(
        'checkbox', 'left', 'default',
        title='Collection Type',
        hidden=False,
        index='collectionType',
        operator='or',
        vocabulary=COLLECTION_VOCAB_NAME,
        count=False,
        maxitems=5,
        sortreversed=False,
        hidezerocount=False,
    )
    criteria.add(
        'checkbox', 'left', 'default',
        title='Site',
        hidden=False,
        index='siteName',
        operator='or',
        vocabulary=u'eke.specimens.vocab.SitesWithSpecimens',
        count=False,
        maxitems=5,
        sortreversed=False,
        hidezerocount=False,
    )
    criteria.add(
        'checkbox', 'bottom', 'default',
        title='Obj provides',
        hidden=True,
        index='object_provides',
        operator='or',
        vocabulary=u'eea.faceted.vocabularies.ObjectProvides',
        default=[ISpecimenSet.__identifier__],
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False
    )
    criteria.add(
        'text', 'center', 'default',
        title='Open Search',
        hidden=False,
        index='SearchableText',
    )
    criteria.add('path', 'bottom', 'default', title='Path Search', hidden=True, index='path', default=path)
    criteria.add('debug', 'top', 'default', title='Debug Criteria', user='kelly')
    IFacetedLayout(folder).update_layout('faceted_specimens_view')
    alsoProvides(folder, IHidePloneRightColumn)
