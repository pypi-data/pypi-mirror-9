# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Biomarker: study statistics implementation.'''

from eke.biomarker import ProjectMessageFactory as _
from eke.biomarker.config import PROJECTNAME
from eke.biomarker.content.base import predicateURIBase
from eke.biomarker.interfaces import IStudyStatistics
from eke.knowledge.content.knowledgeobject import KnowledgeObject
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements

StudyStatisticsSchema = KnowledgeObject.schema.copy() + atapi.Schema((
    atapi.FloatField(
        'sensitivity',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u'Sensitivity'),
            description=_(u'Proportion of actual positives that are correctly identified.'),
        ),
        predicateURI=predicateURIBase + 'Sensitivity',
    ),
    atapi.FloatField(
        'specificity',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u'Specificity'),
            description=_(u'Proportion of actual negatives that are correctly identified.'),
        ),
        predicateURI=predicateURIBase + 'Specificity',
    ),
    atapi.FloatField(
        'npv',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u'NPV'),
            description=_(u'Ratio of true negatives to combined true and false negatives.'),
        ),
        predicateURI=predicateURIBase + 'NPV',
    ),
    atapi.FloatField(
        'ppv',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u'PPV'),
            description=_(u'Ratio of true positives to combined true and false positives.'),
        ),
        predicateURI=predicateURIBase + 'PPV',
    ),
    atapi.FloatField(
        'prevalence',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.DecimalWidget(
            label=_(u'Prevalence'),
            description=_(u'A percentage.'),
        ),
        predicateURI=predicateURIBase + 'Prevalence',
    ),
    atapi.StringField(
        'details',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Details'),
            description=_(u'Detailed notes about this set of statistics.'),
        ),
        predicateURI=predicateURIBase + 'SensSpecDetail',
    ),
    atapi.StringField(
        'specificAssayType',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
           label=_(u'Specific Assay Type'),
           description=_(u'Information about the specific assay used.'),
        ),
        predicateURI=predicateURIBase + 'SpecificAssayType',
    ),
))

finalizeATCTSchema(StudyStatisticsSchema, folderish=False, moveDiscussion=False)

class StudyStatistics(KnowledgeObject):
    '''Study statistics.'''
    implements(IStudyStatistics)
    schema      = StudyStatisticsSchema
    portal_type = 'Study Statistics'
    sensitivity = atapi.ATFieldProperty('sensitivity')
    specificity = atapi.ATFieldProperty('specificity')
    npv         = atapi.ATFieldProperty('npv')
    ppv         = atapi.ATFieldProperty('ppv')
    prevalence  = atapi.ATFieldProperty('prevalence')
    details     = atapi.ATFieldProperty('details')
    specificAssayType = atapi.ATFieldProperty('specificAssayType')

    
atapi.registerType(StudyStatistics, PROJECTNAME)
