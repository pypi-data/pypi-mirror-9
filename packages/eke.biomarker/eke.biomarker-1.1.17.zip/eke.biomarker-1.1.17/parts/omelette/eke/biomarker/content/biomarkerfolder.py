# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Biomarker folder.'''

from eea.facetednavigation.interfaces import IPossibleFacetedNavigable
from eke.biomarker import ProjectMessageFactory as _
from eke.biomarker.config import PROJECTNAME
from eke.biomarker.interfaces import IBiomarkerFolder
from eke.biomarker.utils import setFacetedNavigation
from eke.knowledge.content import knowledgefolder
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements

BiomarkerFolderSchema = knowledgefolder.KnowledgeFolderSchema.copy() + atapi.Schema((
    atapi.StringField(
        'bmoDataSource',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Biomarker-Organ RDF Data Source'),
            description=_(u'URL to a source of RDF data that supplements the RDF data source with biomarker-organ data.'),
            size=60,
        ),
    ),
    atapi.TextField(
        'disclaimer',
        required=False,
        storage=atapi.AnnotationStorage(),
        searchable=False,
        validators=('isTidyHtmlWithCleanup',),
        default_output_type='text/x-html-safe',
        widget=atapi.RichWidget(
            label=_(u'Disclaimer'),
            description=_(u'Legal disclaimer to display on Biomarker Folder pages.'),
            rows=10,
        )
    ),
))

finalizeATCTSchema(BiomarkerFolderSchema, folderish=True, moveDiscussion=False)

class BiomarkerFolder(knowledgefolder.KnowledgeFolder):
    '''Biomarker folder which contains biomarkers.'''
    implements(IBiomarkerFolder, IPossibleFacetedNavigable)
    portal_type               = 'Biomarker Folder'
    _at_rename_after_creation = True
    schema                    = BiomarkerFolderSchema
    bmoDataSource             = atapi.ATFieldProperty('bmoDataSource')
    disclaimer                = atapi.ATFieldProperty('disclaimer')

atapi.registerType(BiomarkerFolder, PROJECTNAME)

def addFacetedNavigation(obj, event):
    '''Set up faceted navigation on all newly created Biomarker Folders.'''
    if not IBiomarkerFolder.providedBy(obj): return
    factory = getToolByName(obj, 'portal_factory')
    if factory.isTemporary(obj): return
    request = obj.REQUEST
    setFacetedNavigation(obj, request)
