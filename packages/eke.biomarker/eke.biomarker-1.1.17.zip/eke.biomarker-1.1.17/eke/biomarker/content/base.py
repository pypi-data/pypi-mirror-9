# encoding: utf-8
# Copyright 2009–2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Biomarker: base content implementation.'''

from eke.biomarker import ProjectMessageFactory as _
from eke.biomarker.interfaces import IBiomarker
from eke.knowledge.content import knowledgeobject
from Products.Archetypes import atapi
from Products.ATContentTypes.content.folder import ATFolder
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

predicateURIBase = 'http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#'

QualityAssuredObjectSchema = atapi.Schema((
    atapi.StringField(
        'qaState',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(
            label=_(u'QA State'),
            description='The current status with regard to quality assurance of this object.',
        ),
        predicateURI=predicateURIBase + 'QAState',
    ),
))

PhasedObjectSchema = atapi.Schema((
    atapi.StringField(
        'phase',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(
            label=_(u'Phase'),
            description=_(u"The current phase of the biomarker's development with regard to this organ."),
        ),
        predicateURI=predicateURIBase + 'Phase',
    ),
))

ResearchedObjectSchema = atapi.Schema((
    atapi.ReferenceField(
        'protocols',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.study.ProtocolsVocabulary',
        relationship='protocolsResearchingThisObject',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Protocols & Studies'),
            description=_(u'Protocols and studies that are studying this object.'),
        ),
        predicateURI=predicateURIBase + 'referencesStudy',
    ),
    atapi.ReferenceField(
        'publications',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.publications.PublicationsVocabulary',
        relationship='publicationsAboutThisObject',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Publications'),
            description=_(u'Publications that have been written talking about this object.'),
        ),
        predicateURI=predicateURIBase + 'referencedInPublication',
    ),
    atapi.ReferenceField(
        'resources',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.knowledge.ResourcesVocabulary',
        relationship='resourcesRelatedToThisObjec',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Resources'),
            description=_(u'Additional resources about this object.'),
        ),
        predicateURI=predicateURIBase + 'referencesResource',
    ),
    atapi.ReferenceField(
        'datasets',
        storage=atapi.AnnotationStorage(),
        enforceVocabulary=True,
        multiValued=True,
        vocabulary_factory=u'eke.ecas.DatasetsVocabulary',
        relationship='datasetsSupportingThisObject',
        vocabulary_display_path_bound=-1,
        widget=atapi.ReferenceWidget(
            label=_(u'Datasets'),
            description=_(u'Datasets providing measured scientific bases for this object.'),
        ),
        predicateURI=predicateURIBase + 'AssociatedDataset',
    ),
))

BiomarkerSchema = knowledgeobject.KnowledgeObjectSchema.copy() + ResearchedObjectSchema.copy() + ATFolder.schema.copy() \
    + atapi.Schema((
    atapi.StringField(
        'shortName',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(
            label=_(u'Short Name'),
            description=_(u'A shorter and preferred alias for the biomarker'),
        ),
        predicateURI=predicateURIBase + 'ShortName',
    ),
    atapi.StringField(
        'hgncName',
        storage=atapi.AnnotationStorage(),
        required=False,
        widget=atapi.StringWidget(
            label=_(u'HGNC Name'),
            description=_(u'The name assigned by the HUGO Gene Nomenclature Committee.'),
        ),
        predicateURI=predicateURIBase + 'HgncName',
    ),
    atapi.LinesField(
        'bmAliases',
        storage=atapi.AnnotationStorage(),
        required=False,
        multiValued=True,
        searchable=True,
        widget=atapi.LinesWidget(
            label=_(u'Aliases'),
            description=_(u'Additional names by which the biomarker is known.'),
        ),
        predicateURI=predicateURIBase + 'Alias'
    ),
    atapi.LinesField(
        'indicatedBodySystems',
        storage=atapi.AnnotationStorage(),
        required=False,
        multiValued=True,
        searchable=True,
        widget=atapi.LinesWidget(
            label=_(u'Indicated Organs'),
            description=_(u'Organs for which this biomarker is an indicator.'),
            visible={'view': 'invisible', 'edit': 'invisible'},
        ),
    ),
    atapi.ComputedField(
        'biomarkerKind',
        searchable=True,
        required=False,
        expression='u"Biomarker"',
        modes=('view',),
        widget=atapi.ComputedWidget(
            visible={'edit': 'invisible', 'view': 'invisible'},
        ),
    ),
    atapi.LinesField(
        'accessGroups',
        storage=atapi.AnnotationStorage(),
        required=False,
        multiValued=True,
        widget=atapi.LinesWidget(
            label=_(u'Access Groups'),
            description=_(u'URIs identifying groups that may access this biomarker.'),
        ),
    ),
))

# FIXME: These should probably both be Dublin Core some day:
BiomarkerSchema['title'].predicateURI = predicateURIBase + 'Title'
BiomarkerSchema['description'].predicateURI = predicateURIBase + 'Description'

class Biomarker(ATFolder, knowledgeobject.KnowledgeObject):
    '''Biomarker.'''
    implements(IBiomarker)
    schema               = BiomarkerSchema
    accessGroups         = atapi.ATFieldProperty('accessGroups')
    biomarkerKind        = atapi.ATFieldProperty('biomarkerKind')
    bmAliases            = atapi.ATFieldProperty('bmAliases')
    description          = atapi.ATFieldProperty('description')
    indicatedBodySystems = atapi.ATFieldProperty('indicatedBodySystems')
    protocols            = atapi.ATReferenceFieldProperty('protocols')
    publications         = atapi.ATReferenceFieldProperty('publications')
    resources            = atapi.ATReferenceFieldProperty('resources')
    datasets             = atapi.ATReferenceFieldProperty('datasets')
    shortName            = atapi.ATFieldProperty('shortName')
    hgncName             = atapi.ATFieldProperty('hgncName')
    def _computeIndicatedBodySystems(self):
        return [i.capitalize() for i in self.objectIds()]
    def updatedIndicatedBodySystems(self):
        self.indicatedBodySystems = self._computeIndicatedBodySystems()
    def SearchableText(self):
        txt = super(Biomarker, self).SearchableText()
        certifications = ''
        for objID, obj in self.contentItems():
            if obj.cliaCertification:
                certifications += 'CLIA ' * 5
            if obj.fdaCertification:
                certifications += 'FDA ' * 20
        return certifications + txt

def BiomarkerVocabularyFactory(context):
    '''Yield a vocabulary for biomarkers.'''
    catalog = getToolByName(context, 'portal_catalog')
    # TODO: filter by review_state?
    results = catalog(object_provides=IBiomarker.__identifier__, sort_on='sortable_title')
    terms = [SimpleVocabulary.createTerm(i.UID, i.UID, i.Title.decode('utf-8')) for i in results]
    return SimpleVocabulary(terms)
directlyProvides(BiomarkerVocabularyFactory, IVocabularyFactory)

def BodySystemUpdater(context, event):
    context.updatedIndicatedBodySystems()
    # We need to update the indicatedBodySystems index, but also SearchableText for certifications,
    # so just do the whole object.
    context.reindexObject()

def IndicatedOrgansVocabularyFactory(context):
    '''Get a vocab for indicated organs'''
    catalog = getToolByName(context, 'portal_catalog')
    results = catalog.uniqueValuesFor('indicatedBodySystems')
    return SimpleVocabulary.fromItems([(i.decode('utf-8'), i.decode('utf-8')) for i in results])
directlyProvides(IndicatedOrgansVocabularyFactory, IVocabularyFactory)    
