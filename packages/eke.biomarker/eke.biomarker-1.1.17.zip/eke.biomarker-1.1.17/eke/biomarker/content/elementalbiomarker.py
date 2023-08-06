# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Biomarker: elemental biomarker implementation.'''

from base import Biomarker, QualityAssuredObjectSchema, predicateURIBase
from eke.biomarker import ProjectMessageFactory as _
from eke.biomarker.config import PROJECTNAME
from eke.biomarker.interfaces import IElementalBiomarker
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from zope.interface import implements

ElementalBiomarkerSchema = Biomarker.schema.copy() + QualityAssuredObjectSchema.copy() + atapi.Schema((
    atapi.StringField(
        'biomarkerType',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(
            label=_(u'Biomarker Type'),
            description=_(u'The general category, kind, or class of this biomarker.'),
        ),
        predicateURI=predicateURIBase + 'Type',
    ),
))

finalizeATCTSchema(ElementalBiomarkerSchema, folderish=True, moveDiscussion=False)

class ElementalBiomarker(Biomarker):
    '''Elemental biomarker.'''
    implements(IElementalBiomarker)
    schema               = ElementalBiomarkerSchema
    portal_type          = 'Elemental Biomarker'
    biomarkerType        = atapi.ATFieldProperty('biomarkerType')
    qaState              = atapi.ATFieldProperty('qaState')

atapi.registerType(ElementalBiomarker, PROJECTNAME)
