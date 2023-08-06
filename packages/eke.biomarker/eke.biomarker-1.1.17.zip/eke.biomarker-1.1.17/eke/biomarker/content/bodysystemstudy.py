# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Biomarker: body system study implementation.'''

from eke.biomarker import ProjectMessageFactory as _
from eke.biomarker.config import PROJECTNAME
from eke.biomarker.content.base import predicateURIBase, ResearchedObjectSchema, PhasedObjectSchema
from eke.biomarker.interfaces import IBodySystemStudy
from eke.knowledge.content.knowledgeobject import KnowledgeObject
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements
from Products.ATContentTypes.content.folder import ATFolder

BodySystemStudySchema = KnowledgeObject.schema.copy() + ResearchedObjectSchema.copy() + ATFolder.schema.copy() + atapi.Schema((
    atapi.ReferenceField(
        'protocol',
        enforceVocabulary=True,
        multiValued=False,
        relationship='protocolStudyingBiomarkerThatIndicatesForAnOrgan',
        required=True,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.study.ProtocolsVocabulary',
        widget=atapi.ReferenceWidget(
            label=_(u'Protocol'),
            description=_(u'The protocol or study that analyzed the organ for which the biomarker indicates diseases.'),
        ),
        predicateURI=predicateURIBase + 'referencesStudy',
    ),
    atapi.StringField(
        'decisionRule',
        required=False,
        searchable=True,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
           label=_(u'Decision Rule'),
           description=_(u'Details about the decision rule for this study')
        ),
        predicateURI=predicateURIBase + 'DecisionRule',
    ),
))

finalizeATCTSchema(BodySystemStudySchema, folderish=True, moveDiscussion=False)

class BodySystemStudy(ATFolder, KnowledgeObject):
    '''Body system study.'''
    implements(IBodySystemStudy)
    schema       = BodySystemStudySchema
    portal_type  = 'Body System Study'
    protocol     = atapi.ATReferenceFieldProperty('protocol')
    protocols    = atapi.ATReferenceFieldProperty('protocols')
    publications = atapi.ATReferenceFieldProperty('publications')
    resources    = atapi.ATReferenceFieldProperty('resources')
    datasets     = atapi.ATReferenceFieldProperty('datasets')
    study        = atapi.ATReferenceFieldProperty('study')
    decisionRule = atapi.ATFieldProperty('decisionRule')
    
atapi.registerType(BodySystemStudy, PROJECTNAME)
