# encoding: utf-8
# Copyright 2009–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Publications: tests of the setup of this package.
'''

from eea.facetednavigation.interfaces import IPossibleFacetedNavigable
from eke.publications.content.publicationfolder import PublicationFolder
from eke.publications.testing import EKE_PUBLICATIONS_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
import unittest2 as unittest

class SetupTest(unittest.TestCase):
    '''Unit tests the setup of this package.'''
    layer = EKE_PUBLICATIONS_INTEGRATION_TESTING
    def setUp(self):
        super(SetupTest, self).setUp()
        self.portal = self.layer['portal']
    def testCatalogIndexes(self):
        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes = catalog.indexes()
        for i in ('authors', 'year', 'abstract'):
            self.failUnless(i in indexes, '%s not found in catalog indexes' % i)
    def testCatalogMetadata(self):
        u'''Check that we have the right metadata columns.'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        columns = catalog.schema()
        for i in ('authors', 'year', 'journal'):
            self.failUnless(i in columns, u'Missing column "{}" in portal_catalog'.format(i))
    def testFacetNavigability(self):
        '''Ensure the Publications Folder type can use faceted navigation.'''
        self.failUnless(IPossibleFacetedNavigable.implementedBy(PublicationFolder))
    def testDiscussion(self):
        '''Ensure discussion is not allowed (CA-1229)'''
        types = getToolByName(self.portal, 'portal_types')
        for i in ('Publication', 'Publication Folder'):
            self.failIf(types[i].allow_discussion, 'Type "%s" allows discussion but it should not' % i)

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
