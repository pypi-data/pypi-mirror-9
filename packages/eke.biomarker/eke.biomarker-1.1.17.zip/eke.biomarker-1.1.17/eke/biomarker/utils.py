# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from zope.component import getMultiAdapter
from zope.interface import noLongerProvides
from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eea.facetednavigation.settings.interfaces import IHidePloneLeftColumn, IHidePloneRightColumn
from eke.biomarker.interfaces import IBiomarker
import plone.api

COLLABORATIVE_GROUP_BMDB_IDS_TO_NAMES = {
    u'Breast and Gynecologic':          u'Breast and Gynecologic Cancers Research Group',
    u'G.I. and Other Associated':       u'G.I. and Other Associated Cancers Research Group',
    u'Lung and Upper Aerodigestive':    u'Lung and Upper Aerodigestive Cancers Research Group',
    u'Prostate and Urologic':           u'Prostate and Urologic Cancers Research Group',
}

def setFacetedNavigation(folder, request, force=False):
    subtyper = getMultiAdapter((folder, request), name=u'faceted_subtyper')
    if (subtyper.is_faceted or not subtyper.can_enable) and not force: return
    subtyper.enable()
    urlTool = plone.api.portal.get_tool(name='portal_url')
    path = '/' + '/'.join(urlTool.getRelativeContentPath(folder))
    criteria = ICriteria(folder)
    for cid in criteria.keys():
        criteria.delete(cid)
    criteria.add(
        'checkbox', 'left', 'default',
        title=u'Organ',
        hidden=False,
        index='indicatedBodySystems',
        operator='or',
        vocabulary=u'eke.biomarker.IndicatedOrgansVocabulary',
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False,
    )
    criteria.add('resultsperpage', 'bottom', 'default', title='Results per page', hidden=True, start=0, end=50, step=5, default=20)
    criteria.add('sorting', 'bottom', 'default', title='Sort on', hidden=True, default='sortable_title')
    criteria.add(
        'checkbox', 'bottom', 'default',
        title='Obj provides',
        hidden=True,
        index='object_provides',
        operator='or',
        vocabulary=u'eea.faceted.vocabularies.ObjectProvides',
        default=[IBiomarker.__identifier__],
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False
    )
    criteria.add('path', 'bottom', 'default', title='Path Search', hidden=True, index='path', default=path)
    criteria.add('debug', 'top', 'default', title='Debug Criteria', user='kelly')
    criteria.add('text', 'top', 'default', title=u'Search', hidden=False, index='SearchableText', count=False,
        onlyallelements=True)
    IFacetedLayout(folder).update_layout('faceted_biomarkers_view')
    noLongerProvides(folder, IHidePloneLeftColumn)
    noLongerProvides(folder, IHidePloneRightColumn)
    