# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.knowledge.testing import EKE_KNOWLEDGE_FIXTURE
from plone.app.testing import PloneSandboxLayer, PLONE_FIXTURE, IntegrationTesting, FunctionalTesting
from plone.app.testing import TEST_USER_ID, TEST_USER_NAME
from plone.testing import z2

class EKEPublications(PloneSandboxLayer):
    defaultBases = (EKE_KNOWLEDGE_FIXTURE,)
    def setUpZope(self, app, configurationContext):
        import eke.publications
        self.loadZCML(package=eke.publications)
        z2.installProduct(app, 'eke.publications')
        import eke.publications.tests.base
        eke.publications.tests.base.registerLocalTestData()
    def setUpPloneSite(self, portal):
        self.applyProfile(portal, 'eke.publications:default')
    def tearDownZope(self, app):
        z2.uninstallProduct(app, 'eke.publications')

EKE_PUBLICATIONS_FIXTURE = EKEPublications()
EKE_PUBLICATIONS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(EKE_PUBLICATIONS_FIXTURE,),
    name='EKEPublications:Integration',
)
EKE_PUBLICATIONS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(EKE_PUBLICATIONS_FIXTURE,),
    name='EKEPublications:Functional',
)
