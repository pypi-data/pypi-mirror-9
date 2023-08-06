# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.knowledge.testing import EKE_KNOWLEDGE_FIXTURE
from plone.app.testing import PloneSandboxLayer, IntegrationTesting, FunctionalTesting
from plone.testing import z2
from Products.CMFCore.utils import getToolByName

class EKEECAS(PloneSandboxLayer):
    defaultBases = (EKE_KNOWLEDGE_FIXTURE,)
    def setUpZope(self, app, configurationContext):
        import eke.ecas
        self.loadZCML(package=eke.ecas)
        z2.installProduct(app, 'eke.ecas')
        
        # More mystery
        import eke.study
        self.loadZCML(package=eke.study)
        z2.installProduct(app, 'eke.study')
        import eke.site
        self.loadZCML(package=eke.site)
        z2.installProduct(app, 'eke.site')
        import eke.publications
        self.loadZCML(package=eke.publications)
        z2.installProduct(app, 'eke.publications')

        import eke.ecas.tests.base
        eke.ecas.tests.base.registerLocalTestData()
    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'eke.ecas:default')
        wfTool = getToolByName(portal, 'portal_workflow')
        wfTool.setDefaultChain('plone_workflow')
    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'eke.ecas')

EKE_ECAS_FIXTURE = EKEECAS()
EKE_ECAS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EKE_ECAS_FIXTURE,),
    name='EKEECAS:Integration',
)
EKE_ECAS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EKE_ECAS_FIXTURE,),
    name='EKEECAS:Functional',
)
