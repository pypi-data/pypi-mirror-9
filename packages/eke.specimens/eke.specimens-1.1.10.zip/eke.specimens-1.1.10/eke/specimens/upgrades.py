# encoding: utf-8
# Copyright 2011–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from interfaces import ISpecimenSystemFolder
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from utils import setFacetedNavigation
from eke.specimens import locateData, PACKAGE_NAME, PROFILE_ID
import logging

COLON_SET_DESCRIPTION = u'''The Early Detection Research Network and the Great Lakes-New England Clinical, Epidemiological and Validation Center (GLNE CEVC) announces the availability of serum, plasma and urine samples for the early detection for colon cancer.'''
LUNG_SET_A_DESCRIPTION = u'''Reference set A focuses on pre-validation of biomarkers of diagnosis of lung cancer and target lung cancer diagnosed for individuals at high risk for lung cancer or abnormal chest x-ray (CXR) or chest computer tomography (CT) but outside of the context of a CT screening trial. The clinical question to be tested after pre-validation relates to whether a serum/plasma biomarker has added value to current clinical tests (CT scan and/or PET scan) for the diagnostic evaluation of pulmonary nodules and to whether such a biomarker could reduce the number, and the attendant cost, of unnecessary invasive tests (PET or tissue biopsy) or futile thoracotomies.'''
LUNG_SET_B_DESCRIPTION = u'''Reference set B focus on pre-validation of biomarkers of early diagnosis (screening) of lung cancer and targeting a specific population of lung cancer patients diagnosed in the context of a computed tomography (CT)-based screening trial of high risk individuals. The clinical question to be tested after pre-validation relates to whether a serum/plasma biomarker has added diagnostic value to current tests (CT scan and/or PET scan) for the diagnostic evaluation of CT-detected pulmonary nodules.'''

def _doPublish(item, wfTool):
    '''Publish item and all its progeny using the given workflow tool.'''
    try:
        wfTool.doActionFor(item, action='publish')
        item.reindexObject()
    except WorkflowException:
        pass
    for i in item.objectIds():
        subItem = item[i]
        _doPublish(subItem, wfTool)

def nullUpgradeStep(setupTool):
    '''A null step for when a profile upgrade requires no custom activity.'''

def _getProtocolUID(portal, identifier):
    catalog = getToolByName(portal, 'portal_catalog')
    results = catalog(identifier=identifier)
    return results[0].UID if len(results) > 0 else None


def addSampleSpecimenSets(setupTool):
    '''Add sample specimen sets'''
    portal = getToolByName(setupTool, 'portal_url').getPortalObject()
    if 'specimens' in portal.keys():
        portal.manage_delObjects('specimens')
    specimens = portal[portal.invokeFactory('Specimen System Folder', 'specimens')]
    specimens.setTitle(u'Specimens')
    specimens.setDescription(u'Specimens collected by EDRN and shared with EDRN.')
    specimens.setText(u'<p>This folder contains specimens available to EDRN and collected in EDRN protocols.</p>')
    
    # Create a place for ERNE
    erne = specimens[specimens.invokeFactory('ERNE Specimen System', 'erne')]
    erne.setTitle(u'EDRN Specimen System')
    erne.setDescription(u'Early Detection Research Network (EDRN) Resource Network Exchange (ERNE) specimens.')
    erne.setText(u'<p>Includes sites running ERNE product servers as well as other EDRN and affiliate specimen collections.</p>')

    # Add reference sets and offline ERNE sites
    specimens._importObjectFromFile(locateData('reference-sets'))
    specimens._importObjectFromFile(locateData('offline-site-specimen-summaries'))

    # Publish it all, add the facets, and we're outta here.
    _doPublish(specimens, getToolByName(portal, 'portal_workflow'))
    addFacetedSearch(setupTool)


def addFacetedSearch(setupTool):
    portal = getToolByName(setupTool, 'portal_url').getPortalObject()
    request = portal.REQUEST
    catalog = getToolByName(setupTool, 'portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=ISpecimenSystemFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the EDRN portal typically includes
        # one Specimen Collection, created above in ``addSampleSpecimenSets`` in fact!
        if 'specimens' in portal.keys():
            results = [portal['specimens']]
    for specimenCollection in results:
        setFacetedNavigation(specimenCollection, request)


def updateDiagnosisIndex(setupTool):
    '''Drop cancerDiagnosis, use diagnosis.'''
    catalog = getToolByName(setupTool, 'portal_catalog')
    schema, indexes = catalog.schema(), catalog.indexes()
    if 'cancerDiagnosis' in schema:
        catalog.delColumn('cancerDiagnosis')
    if 'cancerDiagnosis' in indexes:
        catalog.delIndex('cancerDiagnosis')
    if 'diagnosis' not in indexes:
        catalog.addIndex('diagnosis', 'FieldIndex', {'indexed_attrs': 'diagnosis'})

def setupCatalog(setupTool, logger=None):
    if logger is None: logger = logging.getLogger(PACKAGE_NAME)
    logger.info('Running catalog import-step from profile')
    setupTool.runImportStepFromProfile(PROFILE_ID, 'catalog')
    logger.info('Catalog import-step from profile ran')
