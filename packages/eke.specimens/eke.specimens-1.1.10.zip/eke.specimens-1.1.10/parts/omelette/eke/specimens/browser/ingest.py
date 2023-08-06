# encoding: utf-8
# Copyright 2010 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EDRN Knowledge Environment Specimens: ingest of specimen data.
'''

from Acquisition import aq_inner
from eke.site.interfaces import ISite
from eke.study.interfaces import IProtocol
from eke.specimens import safeInt
from eke.specimens.interfaces import IERNESpecimenSystem, IActiveERNESet
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from utils import getSpecimens, SITES
from views import getOrganLabel
from zope.component import queryUtility

_protocolPrefix = u'http://edrn.nci.nih.gov/data/protocols/'

# Hard-coded contact information for specimens (CA-823) FIXME: This is DISGUSTING.
_contactInfo = {
    'http://edrn.nci.nih.gov/data/sites/167': ('agaitherdavis@hotmail.com', 'A. Gaither Davis'),     # Pittsburgh
    'http://edrn.nci.nih.gov/data/sites/84':  ('William.Rom@nyumc.org', 'William Rom'),              # NYU
    'http://edrn.nci.nih.gov/data/sites/189': ('susil.rayamajhi@ucsfmedctr.org', 'Susil Rayamajhi'), # UCSF
    'http://edrn.nci.nih.gov/data/sites/202': ('Joellen.Weaver@fccc.edu', 'Joellen Weaver'),         # Fox Chase
    'http://edrn.nci.nih.gov/data/sites/203': ('mconnor@bidmc.harvard.edu', 'Marybeth Connors'),     # Beth Israel
    'http://edrn.nci.nih.gov/data/sites/408': ('rschwab@ucsd.edu', 'Richard Schwab'),                # UCSD
    'http://edrn.nci.nih.gov/data/sites/67':  ('dbrenner@umich.edu', 'Dean Brenner'),                # GLNE Dartmouth
    'http://edrn.nci.nih.gov/data/sites/70':  ('dcramer@partners.org', 'Daniel Cramer'),             # Brigham & Women's
    'http://edrn.nci.nih.gov/data/sites/73':  ('wilbur.franklin@uchsc.edu', 'Wilbur Franklin'),      # Colorado
    'http://edrn.nci.nih.gov/data/sites/80':  ('patrice@creighton.edu', 'Patrice Watson'),           # Creighton
    'http://edrn.nci.nih.gov/data/sites/81':  ('ander045@mc.duke.edu', 'Susan Anderson'),            # Duke Univ
    'http://edrn.nci.nih.gov/data/sites/83':  ('ehumphr3@jhmi.edu', 'Elizabeth Humphreys'),          # Johns Hopkins Urology
    'http://edrn.nci.nih.gov/data/sites/91':  ('ejq7@cdc.gov', 'Hao Tian'),                          # CDC
    'http://edrn.nci.nih.gov/data/sites/593': ('cili@fhcrc.org', 'Christopher Li'),                  # CERC at FHCRC
}

class ERNESpecimenSystemViewIngestor(BrowserView):
    '''Ingest specimen data directly from the ERNE query interface.'''
    template = ViewPageTemplateFile('templates/ingestresults.pt')
    render = True
    def _getTools(self, context):
        '''Return a triple containing the catalog tool, the workflow tool, and a function that can be called
        to normalize object IDs.'''
        catalog, wfTool = getToolByName(context, 'portal_catalog'), getToolByName(context, 'portal_workflow')
        normalize = queryUtility(IIDNormalizer).normalize
        return catalog, wfTool, normalize
    def _doPublish(self, item, wfTool):
        '''Using the given workflow tool ``wfTool``, publish the given item, and all its children.'''
        try:
            wfTool.doActionFor(item, action='publish')
            item.reindexObject()
        except WorkflowException:
            pass
        for i in item.objectIds():
            subItem = item[i]
            self._doPublish(subItem, wfTool)
    def lookupProtocol(self, catalog, protocolID):
        '''Find the UID of the protocol with the given protocolID, or None if not found'''
        results = catalog(identifier=_protocolPrefix + unicode(protocolID), object_provides=IProtocol.__identifier__)
        if len(results) == 0: return None
        return results[0].UID
    def __call__(self):
        '''Do the ingest.'''
        context = aq_inner(self.context)
        # Sanity check 
        if not IERNESpecimenSystem.providedBy(context):
            self.results = [u'Use "ingest" on an ERNE Specimen System only']
            return self.render and self.template() or None

        # Prepare
        log = []
        catalog, wfTool, normalize = self._getTools(context)
        
        # Remove any active ERNE entries since the ingest will re-create them
        erne = context
        results = catalog(
            object_provides=IActiveERNESet.__identifier__,
            path=dict(query='/'.join(erne.getPhysicalPath()), depth=1)
        )
        erne.manage_delObjects([i.id for i in results if i.id])
        
        # For each site:
        for siteID, erneID in SITES.items():
            # Find the site.
            results = catalog(identifier=siteID, object_provides=ISite.__identifier__)
            if len(results) != 1:
                # Not found?  Skip it.  More than one?  Weird, but skip 'em.
                log.append('Exactly one site required for %s, but found %d; skipping' % (siteID, len(results)))
                continue
            site = results[0].getObject()
            siteAbbrevName = site.abbreviation if site.abbreviation else site.title
            
            # Grab summaries of all the specimens at this site.
            summaries = getSpecimens(erneID)
            if len(summaries) == 0:
                # None?  Done.  TODO: Should we clear out any old portal records?
                log.append('Zero specimens returned for %s' % siteID)
                continue
            
            # Create
            recordNum = 0
            for summary in summaries:
                recordNum += 1
                sid = '%s-%d' % (site.siteID, recordNum)
                s = erne[erne.invokeFactory('Active ERNE Set', sid)]
                protocolUID = self.lookupProtocol(catalog, summary.protocolID)
                if protocolUID is not None:
                    s.setProtocol(protocolUID)
                numParticipants = safeInt(summary.numberCases) + safeInt(summary.numberControls)
                s.setTitle(siteAbbrevName)
                s.setDescription(u'Specimens from %d Participants %s at %s' % (numParticipants, s.diagnosis, site.title))
                s.setSite(site.UID())
                s.setStorageType(summary.storageType)
                s.diagnosis      = u'With Cancer' if summary.diagnosis else u'Without Cancer'
                s.numCases       = summary.numberCases
                s.numControls    = summary.numberControls
                s.collectionType = summary.collectionType
                s.organs         = (getOrganLabel(summary.organ, context),)
                s.reindexObject()
            log.append('Created %d sets for site %s' % (recordNum, siteAbbrevName))
        self._doPublish(erne, wfTool)
        self.results = log
        return self.render and self.template() or None
            
