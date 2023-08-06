# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Biomarker: biomarker panel implementation.'''

from base import Biomarker, QualityAssuredObjectSchema, predicateURIBase
from eke.biomarker import ProjectMessageFactory as _
from eke.biomarker.config import PROJECTNAME
from eke.biomarker.interfaces import IBiomarkerPanel
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements

BiomarkerPanelSchema = Biomarker.schema.copy() + QualityAssuredObjectSchema.copy() + atapi.Schema((
    atapi.ReferenceField(
        'members',
        enforceVocabulary=True,
        multiValued=True,
        relationship='panelComposition',
        required=False,
        storage=atapi.AnnotationStorage(),
        vocabulary_display_path_bound=-1,
        vocabulary_factory=u'eke.biomarker.BiomarkersVocabulary',
        widget=atapi.ReferenceWidget(
            label=_(u'Member Markers'),
            description=_(u'Biomarkers that are a part of this panel.'),
        ),
    ),
))

finalizeATCTSchema(BiomarkerPanelSchema, folderish=True, moveDiscussion=False)

class BiomarkerPanel(Biomarker):
    '''Biomarker panel.'''
    implements(IBiomarkerPanel)
    schema      = BiomarkerPanelSchema
    portal_type = 'Biomarker Panel'
    members     = atapi.ATReferenceFieldProperty('members')
    qaState     = atapi.ATFieldProperty('qaState')

atapi.registerType(BiomarkerPanel, PROJECTNAME)
