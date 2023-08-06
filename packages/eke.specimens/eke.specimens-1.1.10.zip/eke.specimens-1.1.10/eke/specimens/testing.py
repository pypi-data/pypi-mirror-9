# encoding: utf-8
# Copyright 2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.knowledge.testing import EKE_KNOWLEDGE_FIXTURE
from plone.app.testing import PloneSandboxLayer, IntegrationTesting, FunctionalTesting
from plone.testing import z2
from Products.CMFCore.utils import getToolByName

class EKESpecimens(PloneSandboxLayer):
    defaultBases = (EKE_KNOWLEDGE_FIXTURE,)
    def setUpZope(self, app, configurationContext):
        import eke.specimens
        self.loadZCML(package=eke.specimens)
        z2.installProduct(app, 'eke.specimens')

        # Likewise:
        import eke.publications
        self.loadZCML(package=eke.publications)
        z2.installProduct(app, 'eke.publications')
        import eke.site
        self.loadZCML(package=eke.site)
        z2.installProduct(app, 'eke.site')
        import eke.study
        self.loadZCML(package=eke.study)
        z2.installProduct(app, 'eke.study')

        import eke.specimens.tests.base
        eke.specimens.tests.base.registerLocalTestData()
    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'eke.specimens:default')
        wfTool = getToolByName(portal, 'portal_workflow')
        wfTool.setDefaultChain('plone_workflow')
    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'eke.specimens')

EKE_SPECIMENS_FIXTURE = EKESpecimens()
EKE_SPECIMENS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EKE_SPECIMENS_FIXTURE,),
    name='EKESpecimens:Integration',
)
EKE_SPECIMENS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EKE_SPECIMENS_FIXTURE,),
    name='EKESpecimens:Functional',
)
