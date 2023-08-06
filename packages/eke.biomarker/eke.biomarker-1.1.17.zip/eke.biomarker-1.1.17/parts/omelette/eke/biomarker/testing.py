# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.ecas.testing import EKE_ECAS_FIXTURE
from eke.knowledge.testing import EKE_KNOWLEDGE_FIXTURE
from eke.publications.testing import EKE_PUBLICATIONS_FIXTURE
from eke.site.testing import EKE_SITE_FIXTURE
from eke.study.testing import EKE_STUDY_FIXTURE
from plone.app.testing import PloneSandboxLayer, IntegrationTesting, FunctionalTesting, PLONE_FIXTURE
from plone.testing import z2
from Products.CMFCore.utils import getToolByName

class EKEBiomarker(PloneSandboxLayer):
    defaultBases = (EKE_KNOWLEDGE_FIXTURE,)
    def setUpZope(self, app, configurationContext):
        import eke.biomarker
        self.loadZCML(package=eke.biomarker)
        z2.installProduct(app, 'eke.biomarker')

        # OK, I'm hopeless confused. If I include EKE_PUBLICATIONS_FIXTURE as a base, then teardown fails.
        # So, install it here:
        import eke.publications
        self.loadZCML(package=eke.publications)
        z2.installProduct(app, 'eke.publications')
        # Likewise:
        import eke.site
        self.loadZCML(package=eke.site)
        z2.installProduct(app, 'eke.site')
        # Likewise:
        import eke.study
        self.loadZCML(package=eke.study)
        z2.installProduct(app, 'eke.study')
        # Likewise:
        import eke.ecas
        self.loadZCML(package=eke.ecas)
        z2.installProduct(app, 'eke.ecas')

        import eke.biomarker.tests.base
        eke.biomarker.tests.base.registerLocalTestData()
    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'eke.biomarker:default')
        wfTool = getToolByName(portal, 'portal_workflow')
        wfTool.setDefaultChain('plone_workflow')
    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'eke.biomarker')

EKE_BIOMARKER_FIXTURE = EKEBiomarker()
EKE_BIOMARKER_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EKE_BIOMARKER_FIXTURE,),
    name='EKEBiomarker:Integration',
)
EKE_BIOMARKER_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EKE_BIOMARKER_FIXTURE,),
    name='EKEBiomarker:Functional',
)
