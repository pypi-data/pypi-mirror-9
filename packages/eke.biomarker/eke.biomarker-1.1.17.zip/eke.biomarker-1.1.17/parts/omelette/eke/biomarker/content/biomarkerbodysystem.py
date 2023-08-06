# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Biomarker: biomarker body system implementation.'''

from eke.biomarker import ProjectMessageFactory as _
from eke.biomarker.config import PROJECTNAME
from eke.biomarker.interfaces import IBiomarkerBodySystem
from eke.biomarker.content.base import ResearchedObjectSchema, PhasedObjectSchema, QualityAssuredObjectSchema, predicateURIBase
from eke.knowledge.content.knowledgeobject import KnowledgeObject
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.ATContentTypes.content.folder import ATFolder
from zope.interface import implements

BiomarkerBodySystemSchema = KnowledgeObject.schema.copy() + QualityAssuredObjectSchema.copy() + PhasedObjectSchema.copy() \
    + ResearchedObjectSchema.copy() + ATFolder.schema.copy() + atapi.Schema((
    atapi.ReferenceField(
        'bodySystem',
        enforceVocabulary=True,
        multiValued=False,
        relationship='bodySystemIndicatesFor',
        required=True,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.knowledge.BodySystems',
        widget=atapi.ReferenceWidget(
            label=_(u'Organ'),
            description=_(u'The organ for which the biomarker indicates diseases.'),
        ),
        # No predicateURI here; the RDF output just names the organ, so we'll have to
        # link it manually during ingest.
    ),
    atapi.StringField(
        'performanceComment',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
           label=_(u'Performance Comment'),
           description=_(u'A description of biomarker performance with respect to this organ'),
        ),
        predicateURI='http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#PerformanceComment',
    ),
    atapi.BooleanField(
        'cliaCertification',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u'CLIA Certification'),
            description=_(u'True if this biomarker has been certified by CLIA for this organ.'),
        ),
    ),
    atapi.BooleanField(
        'fdaCertification',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u'FDA Certification'),
            description=_(u'True if this biomarker has been certified by the FDA for this organ.'),
        ),
    ),
))

# FIXME: This should be a Dublin Core description:
BiomarkerBodySystemSchema['description'].predicateURI = predicateURIBase + 'Description'

finalizeATCTSchema(BiomarkerBodySystemSchema, folderish=True, moveDiscussion=False)

class BiomarkerBodySystem(ATFolder, KnowledgeObject):
    '''Biomarker body system.'''
    implements(IBiomarkerBodySystem)
    schema             = BiomarkerBodySystemSchema
    portal_type        = 'Biomarker Body System'
    bodySystem         = atapi.ATReferenceFieldProperty('bodySystem')
    phase              = atapi.ATFieldProperty('phase')
    protocols          = atapi.ATReferenceFieldProperty('protocols')
    publications       = atapi.ATReferenceFieldProperty('publications')
    qaState            = atapi.ATFieldProperty('qaState')
    resources          = atapi.ATReferenceFieldProperty('resources')
    datasets           = atapi.ATReferenceFieldProperty('datasets')
    description        = atapi.ATFieldProperty('description')
    performanceComment = atapi.ATFieldProperty('performanceComment')
    cliaCertification  = atapi.ATFieldProperty('cliaCertification')
    fdaCertification   = atapi.ATFieldProperty('fdaCertification')
    
atapi.registerType(BiomarkerBodySystem, PROJECTNAME)
