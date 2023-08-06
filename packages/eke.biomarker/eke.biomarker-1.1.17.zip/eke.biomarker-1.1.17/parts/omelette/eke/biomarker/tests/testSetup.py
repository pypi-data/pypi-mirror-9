# encoding: utf-8
# Copyright 2009–2012 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE Biomarker: test the setup of this package.
'''

from eke.biomarker.testing import EKE_BIOMARKER_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
import unittest2 as unittest

class SetupTest(unittest.TestCase):
    '''Unit tests the setup of this package.'''
    layer = EKE_BIOMARKER_INTEGRATION_TESTING
    def setUp(self):
        super(SetupTest, self).setUp()
        self.portal = self.layer['portal']
    def testCatalogIndexes(self):
        '''Check if indexes are properly installed.'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        indexes = catalog.indexes()
        for i in ('biomarkerType', 'indicatedBodySystems', 'accessGroups'):
            self.failUnless(i in indexes)
    def testCatalogMetadata(self):
        '''Check if indexed metadata schema are properly installed.'''
        catalog = getToolByName(self.portal, 'portal_catalog')
        metadata = catalog.schema()
        for i in ('biomarkerType', 'indicatedBodySystems'):
            self.failUnless(i in metadata)
    def testTypes(self):
        '''Make sure our types are available.'''
        types = getToolByName(self.portal, 'portal_types')
        for i in (
            'Biomarker Folder', 'Elemental Biomarker', 'Biomarker Panel', 'Biomarker Body System', 'Body System Study',
            'Study Statistics'
        ):
            self.failUnless(i in types.objectIds())
            self.failIf(types[i].allow_discussion, 'Type "%s" allows discussion, but should not' % i) # CA-1229
    def testObsoleteTypes(self):
        '''Make sure obsolete types are gone.'''
        types = getToolByName(self.portal, 'portal_types').objectIds()
        self.failIf('Review Listing' in types, u'`Review Listing` type is obsolete and should not be implemented anymore')
    def testTypesNotSearched(self):
        '''Ensure our "structural" types aren't searched by default.'''
        notSearched = self.portal.portal_properties.site_properties.getProperty('types_not_searched')
        for i in ('Biomarker Body System', 'Body System Study', 'Study Statistics'):
            self.failUnless(i in notSearched)
    def testForWideURLField(self):
        '''Ensure fields for URLs are extra wide.'''
        from eke.biomarker.content.biomarkerfolder import BiomarkerFolderSchema
        self.failUnless(BiomarkerFolderSchema['bmoDataSource'].widget.size >= 60)
    def testVocabularies(self):
        vocabs = (u'eke.biomarker.BiomarkersVocabulary', u'eke.biomarker.IndicatedOrgansVocabulary')
        for v in vocabs:
            self.failUnless(queryUtility(IVocabularyFactory, name=v), u'Vocabulary "{}" not available'.format(v))



class CollaborativeGroupNamingTest(unittest.TestCase):
    '''Unit tests for the identification of collaborative groups in BMDB'''
    layer = EKE_BIOMARKER_INTEGRATION_TESTING
    def setUp(self):
        super(CollaborativeGroupNamingTest, self).setUp()
        self.portal = self.layer['portal']
    def testGroupNameMapping(self):
        from eke.biomarker.utils import COLLABORATIVE_GROUP_BMDB_IDS_TO_NAMES as cgbitn
        self.assertEquals(u'Breast and Gynecologic Cancers Research Group',         cgbitn[u'Breast and Gynecologic'])
        self.assertEquals(u'G.I. and Other Associated Cancers Research Group',      cgbitn[u'G.I. and Other Associated'])
        self.assertEquals(u'Lung and Upper Aerodigestive Cancers Research Group',   cgbitn[u'Lung and Upper Aerodigestive'])
        self.assertEquals(u'Prostate and Urologic Cancers Research Group',          cgbitn[u'Prostate and Urologic'])

def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
    
