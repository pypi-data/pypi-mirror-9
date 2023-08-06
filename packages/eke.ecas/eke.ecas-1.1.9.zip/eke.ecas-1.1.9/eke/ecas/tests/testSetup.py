# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE ECAS: test the setup of this package.
'''

import unittest2 as unittest
from eke.ecas.testing import EKE_ECAS_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName

class SetupTest(unittest.TestCase):
    '''Unit tests the setup of this package.'''
    layer = EKE_ECAS_INTEGRATION_TESTING    
    def setUp(self):
        super(SetupTest, self).setUp()
        self.portal = self.layer['portal']
    def testCatalogIndexes(self):
        '''Check if indexes are properly installed'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes = catalog.indexes()
        for i in ('bodySystemName', 'protocolName', 'collaborativeGroup', 'piUID', 'getProtocolUID', 'collaborativeGroupUID'):
            self.failUnless(i in indexes)
    def testCatalogMetadata(self):
        '''Check if indexed metadata schema are properly installed'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        metadata = catalog.schema()
        for i in ('bodySystemName', 'protocolName', 'collaborativeGroup', 'piUID', 'getProtocolUID', 'collaborativeGroupUID'):
            self.failUnless(i in metadata)
    def testTypes(self):
        '''Make sure our types are available'''
        types = getToolByName(self.portal, 'portal_types')
        for i in ('Dataset Folder', 'Dataset'):
            self.failUnless(i in types.objectIds(), 'Type "%s" missing' % i)
            self.failIf(types[i].allow_discussion, 'Type "%s" allows discussion but should not' % i)


class CollaborativeGroupNamingTest(unittest.TestCase):
    '''Unit tests for the identification of collaborative groups in ECAS'''
    layer = EKE_ECAS_INTEGRATION_TESTING    
    def setUp(self):
        super(CollaborativeGroupNamingTest, self).setUp()
        self.portal = self.layer['portal']
    def testGroupNameMapping(self):
        from eke.ecas.utils import COLLABORATIVE_GROUP_ECAS_IDS_TO_NAMES as cgitn
        self.assertEquals(u'Breast and Gynecologic Cancers Research Group',         cgitn[u'Breast/GYN'])
        self.assertEquals(u'G.I. and Other Associated Cancers Research Group',      cgitn[u'GI and Other Associated'])
        self.assertEquals(u'Lung and Upper Aerodigestive Cancers Research Group',   cgitn[u'Lung and Upper Aerodigestive'])
        self.assertEquals(u'Prostate and Urologic Cancers Research Group',          cgitn[u'Prostate and Urologic'])

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
