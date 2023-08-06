# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE Biomarkers: RDF ingest for biomarkers.
'''

from Acquisition import aq_inner, aq_parent
from eke.biomarker.interfaces import IBiomarker
from eke.biomarker.utils import COLLABORATIVE_GROUP_BMDB_IDS_TO_NAMES
from eke.knowledge import ProjectMessageFactory as _
from eke.knowledge.browser.rdf import KnowledgeFolderIngestor, CreatedObject, RDFIngestException
from eke.knowledge.browser.utils import updateObject
from eke.knowledge.interfaces import IBodySystem
from eke.study.interfaces import IProtocol
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from rdflib import URIRef, ConjunctiveGraph, URLInputSource
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.publisher.browser import TestRequest
from zExceptions import BadRequest
import uuid, logging

_logger = logging.getLogger(__name__)

# Well-known URI refs
_accessPredicateURI                      = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#AccessGrantedTo')
_biomarkerPredicateURI                   = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Biomarker')
_biomarkerTypeURI                        = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Biomarker')
_bmOrganDataTypeURI                      = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#BiomarkerOrganData')
_bmTitlePredicateURI                     = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Title')
_certificationPredicateURI               = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#certification')
_hasBiomarkerStudyDatasPredicateURI      = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#hasBiomarkerStudyDatas')
_hasBiomarkerOrganStudyDatasPredicateURI = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#hasBiomarkerOrganStudyDatas')
_hgncPredicateURI                        = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#HgncName')
_isPanelPredicateURI                     = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#IsPanel')
_memberOfPanelPredicateURI               = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#memberOfPanel')
_organPredicateURI                       = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#Organ')
_referencesStudyPredicateURI             = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#referencesStudy')
_sensitivityDatasPredicateURI            = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#SensitivityDatas')
_typeURI                                 = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
_visibilityPredicateURI                  = URIRef('http://edrn.nci.nih.gov/rdf/rdfs/bmdb-1.0.0#QAState')

# Certification URIs
_cliaCertificationURI = URIRef('http://www.cms.gov/Regulations-and-Guidance/Legislation/CLIA/index.html')
_fdaCeritificationURI = URIRef('http://www.fda.gov/regulatoryinformation/guidances/ucm125335.htm')

# How many biomarkers we'll tolerate with the same ID before we balk
MAX_NON_UNIQUE_BIOMARKER_IDS = 100

# Interface identifier for EDRN Collaborative Group, from edrnsite.collaborations
_collabGroup = 'edrnsite.collaborations.interfaces.collaborativegroupindex.ICollaborativeGroupIndex'

def flatten(l):
    '''Flatten a list.'''
    for i in l:
        if isinstance(i, list):
            for j in flatten(i):
                yield j
        else:
            yield i

class BiomarkerFolderIngestor(KnowledgeFolderIngestor):
    '''RDF ingestion for biomarkers.'''
    def _pushWorkflow(self, item, wfTool, action='publish'):
        try:
            wfTool.doActionFor(item, action=action)
            item.reindexObject()
        except WorkflowException:
            pass
        for i in item.objectIds():
            subItem = item[i]
            self._pushWorkflow(subItem, wfTool, action)
    def publishBiomarker(self, context, biomarker, predicates):
        wfTool = getToolByName(context, 'portal_workflow')
        if wfTool.getInfoFor(biomarker, 'review_state') != 'published':
            self._pushWorkflow(biomarker, wfTool)
    def retractBiomarker(self, context, biomarker, predicates):
        wfTool = getToolByName(context, 'portal_workflow')
        if wfTool.getInfoFor(biomarker, 'review_state') != 'private':
            self._pushWorkflow(biomarker, wfTool, 'hide')
    def findObjectsByIdentifiers(self, catalog, identifiers):
        '''Use the given catalog to find the given identifiers.  Return a list
        of the matching objects rather than a sequence of brains.'''
        results = catalog(identifier=[unicode(i) for i in identifiers])
        return [i.getObject() for i in results]
    def updateCollaborativeGroups(self, context, biomarker):
        catalog = getToolByName(context, 'portal_catalog')
        for accessGroup in biomarker.accessGroups:
            groupName = COLLABORATIVE_GROUP_BMDB_IDS_TO_NAMES.get(accessGroup)
            if not groupName: continue
            results = [i.getObject() for i in catalog(object_provides=_collabGroup, Title=groupName)]
            for collabGroup in results:
                currentBiomarkers = collabGroup.getBiomarkers()
                if biomarker not in currentBiomarkers:
                    currentBiomarkers.append(biomarker)
                    collabGroup.setBiomarkers(currentBiomarkers)
    def updateBiomarker(self, obj, uri, predicates, context, statements):
        '''Update a biomarker. Sets various attributes and then adjusts workflow & security.'''
        updateObject(obj, uri, predicates, context)
        if _accessPredicateURI in predicates:
            groupIDs = [unicode(i) for i in predicates[_accessPredicateURI]]
            obj.accessGroups = groupIDs
            settings = [dict(type='group', roles=[u'Reader'], id=i) for i in groupIDs]
            sharing = getMultiAdapter((obj, TestRequest()), name=u'sharing')
            sharing.update_role_settings(settings)
            self.updateCollaborativeGroups(context, obj)
        if _hasBiomarkerStudyDatasPredicateURI in predicates:
            catalog = getToolByName(context, 'portal_catalog')
            protocolUIDs = []
            bag = statements[predicates[_hasBiomarkerStudyDatasPredicateURI][0]]
            for subjectURI, objects in bag.iteritems():
                if subjectURI == _typeURI: continue
                # Assume anything else is a list item pointing to BiomarkerStudyData objects
                for bmsd in [statements[i] for i in objects]:
                    # Right now, we use just the "referencesStudy" predicate, if it's present
                    if _referencesStudyPredicateURI not in bmsd: continue
                    results = catalog(
                        identifier=unicode(bmsd[_referencesStudyPredicateURI][0]),
                        object_provides=IProtocol.__identifier__
                    )
                    protocolUIDs.extend([j.UID for j in results])
                    for k in [j.getObject() for j in results]:
                        self._addBiomarkerToProtocol(obj, k)
            obj.setProtocols(protocolUIDs)
    def addStatistics(self, bodySystemStudy, bags, statements, normalizer, catalog):
        '''Add study statistics to a body system study.  The bags are
        RDF-style collections of URIRefs to statistics found in the
        statements.'''
        # Gather all the URIs
        sensitivityURIs = []
        for bag in bags:
            preds = statements[bag]
            del preds[_typeURI]
            sensitivityURIs.extend(flatten(preds.values()))
        # For each set of statistics...
        for sensitivityURI in sensitivityURIs:
            predicates = statements[sensitivityURI]
            stats = bodySystemStudy[bodySystemStudy.invokeFactory('Study Statistics', uuid.uuid1())]
            updateObject(stats, sensitivityURI, predicates, catalog)
            stats.title = sensitivityURI
            stats.reindexObject()
    def _addBiomarkerToProtocol(self, biomarker, protocol):
        uid = biomarker.UID()
        current = [i.UID() for i in protocol.biomarkers]
        if uid not in current:
            current.append(uid)
            protocol.setBiomarkers(current)
    def addStudiesToOrgan(self, biomarkerBodySystem, bags, statements, normalizer, catalog):
        '''Add protocol/study-specific information to a biomarker body system.'''
        # Gather all the URIs
        bmStudyDataURIs = []
        # The RDF may contain an empty <hasBiomarkerStudyDatas/>, which means that
        # there will be just an empty Literal '' in the bags list (which will be a
        # one item list). In that case, don't bother adding studies.
        if len(bags) == 1 and unicode(bags[0]) == u'':
            return
        for bag in bags:
            preds = statements[bag]
            del preds[_typeURI]
            bmStudyDataURIs.extend(flatten(preds.values()))
        for studyURI in bmStudyDataURIs:
            bmStudyDataPredicates = statements[studyURI]
            if _referencesStudyPredicateURI not in bmStudyDataPredicates:
                continue
            studies = self.findObjectsByIdentifiers(catalog,
                [unicode(i) for i in bmStudyDataPredicates[_referencesStudyPredicateURI]])
            if len(studies) < 1:
                _logger.warn('Study "%s" not found for biomarker body system "%r"',
                    bmStudyDataPredicates[_referencesStudyPredicateURI][0],
                    biomarkerBodySystem.identifier
                )
                continue
            identifier = normalizer(studies[0].title)
            bodySystemStudy = biomarkerBodySystem[biomarkerBodySystem.invokeFactory('Body System Study', identifier)]
            updateObject(bodySystemStudy, studyURI, bmStudyDataPredicates, catalog)
            bodySystemStudy.title = studies[0].title
            bodySystemStudy.description = studies[0].description
            bodySystemStudy.setProtocol(studies[0].UID())
            self._addBiomarkerToProtocol(aq_parent(aq_inner(aq_parent(aq_inner(bodySystemStudy)))), studies[0])
            if _sensitivityDatasPredicateURI in bmStudyDataPredicates:
                bags = bmStudyDataPredicates[_sensitivityDatasPredicateURI]
                self.addStatistics(bodySystemStudy, bags, statements, normalizer, catalog)
            bodySystemStudy.reindexObject()
    def addOrganSpecificInformation(self, biomarkers, statements, normalizer, catalog):
        '''Populate biomarkers with body system (aka "organ") details.'''
        for uri, predicates in statements.items():
            try:
                if predicates[_typeURI][0] != _bmOrganDataTypeURI:
                    continue
                biomarker = biomarkers[predicates[_biomarkerPredicateURI][0]]
            except KeyError:
                continue
            organName = unicode(predicates[_organPredicateURI][0])
            results = catalog(Title=organName, object_provides=IBodySystem.__identifier__)
            if len(results) < 1:
                _logger.warn('Unknown organ %s for biomarker %s', organName, biomarker.title)
                continue
            organObjID = normalizer(organName)
            biomarkerBodySystem = biomarker[biomarker.invokeFactory('Biomarker Body System', organObjID)]
            biomarkerBodySystem.setTitle(results[0].Title)
            biomarkerBodySystem.setBodySystem(results[0].UID)
            updateObject(biomarkerBodySystem, uri, predicates, catalog)
            if _hasBiomarkerOrganStudyDatasPredicateURI in predicates:
                bags = predicates[_hasBiomarkerOrganStudyDatasPredicateURI]
                self.addStudiesToOrgan(biomarkerBodySystem, bags, statements, normalizer, catalog)
            certificationURIs = predicates.get(_certificationPredicateURI, [])
            # TODO: make a separate Certification type so we don't rely on these fixed values.
            # Although we'll likely never have ohter certifications.
            for certificationURI in certificationURIs:
                if certificationURI == _cliaCertificationURI:
                    biomarkerBodySystem.cliaCertification = True
                elif certificationURI == _fdaCeritificationURI:
                    biomarkerBodySystem.fdaCertification = True
            biomarkerBodySystem.reindexObject()
    def __call__(self):
        '''Ingest and render a results page.'''
        context = aq_inner(self.context)
        rdfDataSource, bmoDataSource = context.rdfDataSource, context.bmoDataSource
        if not rdfDataSource or not bmoDataSource:
            raise RDFIngestException(_(u'This biomarker folder lacks one or both of its RDF source URLs.'))
        # Weapons at ready
        catalog = getToolByName(context, 'portal_catalog')
        normalizerFunction = queryUtility(IIDNormalizer).normalize
        graph = ConjunctiveGraph()
        graph.parse(URLInputSource(rdfDataSource))
        statements = self._parseRDF(graph)
        # Clean the slate (but not the subfolders)
        results = catalog(path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            object_provides=IBiomarker.__identifier__)
        context.manage_delObjects([i.id for i in results])
        newBiomarkers = {}
        # Make all the biomarker objects
        for uri, predicates in statements.items():
            try:
                typeURI = predicates[_typeURI][0]
                if typeURI != _biomarkerTypeURI:
                    continue
                isPanel = bool(int(predicates[_isPanelPredicateURI][0]))
                title = unicode(predicates[_bmTitlePredicateURI][0])
                hgnc = predicates[_hgncPredicateURI][0] if _hgncPredicateURI in predicates else None
                if hgnc is not None:
                    hgnc = hgnc.strip()
                objID = hgnc if hgnc else normalizerFunction(title)
                objType = isPanel and 'Biomarker Panel' or 'Elemental Biomarker'
                try:
                    obj = context[context.invokeFactory(objType, objID)]
                except BadRequest:
                    obj = None
                    for appendedNumber in xrange(1, MAX_NON_UNIQUE_BIOMARKER_IDS+1):
                        try:
                            obj = context[context.invokeFactory(objType, "%s-%d" % (objID, appendedNumber))]
                            break
                        except BadRequest:
                            pass
                    if obj is None:
                        raise BadRequest("Something's wrong. Got more than %d biomarkers with the same ID '%s'!" %
                            (MAX_NON_UNIQUE_BIOMARKER_IDS, objID))
                self.updateBiomarker(obj, uri, predicates, context, statements)
                newBiomarkers[uri] = obj
                obj.reindexObject()
            except KeyError:
                pass
        # Connect elementals to their panels
        for uri, predicates in statements.items():
            try:
                typeURI = predicates[_typeURI][0]
                if typeURI != _biomarkerTypeURI:
                    continue
                biomarkerUID = newBiomarkers[uri].UID()
                panelURIs = predicates[_memberOfPanelPredicateURI]
                panels = self.findObjectsByIdentifiers(catalog, panelURIs)
                for panel in panels:
                    current = [i.UID() for i in panel.members]
                    current.append(biomarkerUID)
                    panel.setMembers(current)
            except KeyError:
                pass
        # Add organ-specific information
        graph = ConjunctiveGraph()
        graph.parse(URLInputSource(bmoDataSource))
        organStatements = self._parseRDF(graph)
        self.addOrganSpecificInformation(newBiomarkers, organStatements, normalizerFunction, catalog)
        # Update indicated organs:
        for biomarker in newBiomarkers.values():
            biomarker.updatedIndicatedBodySystems()
            biomarker.reindexObject()
        # Publish as necessary
        for uri, predicates in statements.items():
            if uri in newBiomarkers:
                biomarker = newBiomarkers[uri]
                if biomarker.qaState == 'Private':
                    self.retractBiomarker(context, biomarker, predicates)
                else:
                    self.publishBiomarker(context, biomarker, predicates)
        self.objects = [CreatedObject(i) for i in newBiomarkers.values()]
        return self.render and self.template() or len(self.objects)
