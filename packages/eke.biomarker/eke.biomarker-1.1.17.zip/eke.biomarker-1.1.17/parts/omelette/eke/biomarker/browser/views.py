# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE Biomarkers: views for content types.
'''

from Acquisition import aq_inner
from eke.biomarker.interfaces import IBiomarkerFolder, IBiomarker, IBiomarkerBodySystem, IBodySystemStudy, IStudyStatistics, \
    IReviewListing
from eke.knowledge.browser.views import KnowledgeFolderView, KnowledgeObjectView
from plone.memoize.instance import memoize
from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

CURATED_SECTIONS = {
    'Organs': True,
    'Studies': False,
    'Publications': True,
    'Resources': True,
    'Organs-Supplemental': False,
}

class PIsByBiomarkerView(KnowledgeFolderView):
    __call__ = ViewPageTemplateFile('templates/pis_by_biomarker.pt')
    def haveBiomarkers(self):
        return len(self.biomarkers()) > 0
    @memoize
    def biomarkers(self):
        context, biomarkers, allInvestigators = aq_inner(self.context), {}, set()
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(object_provides=IBiomarker.__identifier__, path=dict(query='/'.join(context.getPhysicalPath()), depth=1))
        for i in results:
            biomarker = i.getObject()
            name, qaState, protocols = biomarker.title.strip(), biomarker.qaState, biomarker.getProtocols()
            if len(protocols) == 0: continue
            investigators = set()
            for protocol in protocols:
                if protocol.piName is not None and len(protocol.piName.strip()) > 0:
                    investigators.add(protocol.piName.strip())
                for site in protocol.getInvolvedInvestigatorSites():
                    pi = site.getPrincipalInvestigator()
                    if pi is not None and len(pi.title.strip()) > 0:
                        investigators.add(pi.title.strip())
            allInvestigators |= investigators
            pis = biomarkers.get(name, set())
            pis |= investigators
            biomarkers[name] = pis
        bmNames = biomarkers.keys()
        bmNames.sort()
        finalResults = []
        for bmName in bmNames:
            pis = list(biomarkers[bmName])
            pis.sort()
            finalResults.append(dict(bmName=bmName, pis=pis))
        return finalResults
        

class BiomarkerFolderView(KnowledgeFolderView):
    '''Default view of a Biomarker Folder.'''
    __call__ = ViewPageTemplateFile('templates/biomarkerfolder.pt')
    def haveBiomarkers(self):
        '''Do we even have biomarkers? Return True if so.'''
        return len(self.biomarkers()) > 0
    @memoize
    def biomarkers(self):
        '''Fetcheth me the biomarkers here.'''
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        allBiomarkers = dict([
            (i.UID, dict(
                title=i.Title, description=i.Description, url=i.getURL(), biomarkerType=i.biomarkerType,                
                bodySystems=i.indicatedBodySystems, reviewState='hide'
            )) for i in catalog.search(
                query_request=dict(
                    object_provides=IBiomarker.__identifier__,
                    path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
                )
            )
        ])
        visibleBiomarkers = [
            i.UID for i in catalog.searchResults(
                object_provides=IBiomarker.__identifier__,
                path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            )
        ]
        for i in visibleBiomarkers:
            biomarker = allBiomarkers[i]
            biomarker['reviewState'] = 'published'
        results = allBiomarkers.values()
        results.sort(lambda a, b: cmp(a['title'], b['title']))
        return results
    @memoize
    def subfolders(self):
        '''Fetcheth me the subfolders here.'''
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=IBiomarkerFolder.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(title=i.Title, description=i.Description, url=i.getURL()) for i in results]
    @memoize
    def reviewListings(self):
        '''Fetcheth me the Review Listings here.'''
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=IReviewListing.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(title=i.Title, description=i.Description, url=i.getURL()) for i in results]
    def haveReviewListings(self):
        '''Do we have any review listings?'''
        return len(self.reviewListings()) > 0


class BiomarkerBodySystemView(KnowledgeObjectView):
    '''Default view of a Biomarker Body System.'''
    __call__ = ViewPageTemplateFile('templates/biomarkerbodysystem.pt')

class BiomarkerView(KnowledgeObjectView):
    '''Abstract view of abstract biomarkers.'''
    def bodySystemsAvailable(self):
        return len(self.bodySystems()) > 0
    @memoize
    def bodySystems(self):
        context = aq_inner(self.context)
        catalog = getToolByName(context, 'portal_catalog')
        results = catalog(
            object_provides=IBiomarkerBodySystem.__identifier__,
            path=dict(query='/'.join(context.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        results = [dict(name=i.Title, obj=i.getObject(), resources=list(i.getObject().resources)) for i in results]
        for result in results:
            resources = result['resources']
            resources.sort(lambda a, b: cmp(a.title, b.title))
        return results
    @memoize
    def resources(self):
        context = aq_inner(self.context)
        resources = list(context.resources)
        resources.sort(lambda a, b: cmp(a.title, b.title))
        return resources
    @memoize
    def studies(self, bodySystem):
        catalog = getToolByName(bodySystem, 'portal_catalog')
        results = catalog(
            object_provides=IBodySystemStudy.__identifier__,
            path=dict(query='/'.join(bodySystem.getPhysicalPath()), depth=1),
            sort_on='sortable_title'
        )
        return [dict(name=i.Title, obj=i.getObject()) for i in results]
    @memoize
    def statistics(self, protocol):
        def massage(value, deterministic=True):
            try:
                numeric = float(value)
            except (ValueError, TypeError):
                return u'ND' if deterministic else u'N/A' # ND = Not determined
            if numeric == 0.0:
                return u'N/A' # Not applicable
            return numeric
        catalog = getToolByName(protocol, 'portal_catalog')
        results = catalog(
            object_provides=IStudyStatistics.__identifier__,
            path=dict(query='/'.join(protocol.getPhysicalPath()), depth=1),
            sort_on='getObjPositionInParent'
        )
        return [dict(
            notes=i.getObject().details,
            sens=massage(i.getObject().sensitivity),
            spec=massage(i.getObject().specificity),
            npv=massage(i.getObject().npv, deterministic=False),
            ppv=massage(i.getObject().ppv, deterministic=False),
            prev=massage(i.getObject().prevalence, deterministic=False),
        ) for i in results]
    @memoize
    def viewable(self, section):
        '''Are details from the named ``section`` of this biomarker viewable?'''
        context = aq_inner(self.context)
        # Accepted biomarkers are A-O-K no matter what section.
        if context.qaState == u'Accepted':
            return True
        # Certain sections are viewable for curated-but-not-yet-accepted biomarkers
        if context.qaState == u'Curated':
            canView = CURATED_SECTIONS.get(section, False)
            if canView: return True
        # Anonymous user?  Go away.
        mtool = getToolByName(context, 'portal_membership')
        if mtool.isAnonymousUser():
            return False
        # Manager?  Welcome.
        member = mtool.getAuthenticatedMember()
        if 'Manager' in member.getRoles():
            return True
        # Not a manager?  Check groups.
        gtool = getToolByName(context, 'portal_groups')
        memberGroups = set([i.getGroupId() for i in gtool.getGroupsByUserId(member.getMemberId())])
        objectRoles = dict(context.get_local_roles())
        for groupName, roles in objectRoles.items():
            if u'Reader' in roles and groupName in memberGroups:
                return True
        return False

class BiomarkerPanelView(BiomarkerView):
    '''Default view of a Biomarker Panel.'''
    __call__ = ViewPageTemplateFile('templates/biomarkerpanel.pt')
    
class ElementalBiomarkerView(BiomarkerView):
    '''Default view of an Elemental Biomarker.'''
    __call__ = ViewPageTemplateFile('templates/elementalbiomarker.pt')

class BodySystemStudyView(KnowledgeObjectView):
    '''Default view of a Body System Study.'''
    __call__ = ViewPageTemplateFile('templates/bodysystemstudy.pt')
    
class StudyStatisticsView(KnowledgeObjectView):
    '''Default view of Study Statistics.'''
    __call__ = ViewPageTemplateFile('templates/studystatistics.pt')
    
