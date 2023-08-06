# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.biomarker import PROFILE_ID
from eke.biomarker.interfaces import IBiomarkerFolder
from Products.CMFCore.utils import getToolByName
from utils import setFacetedNavigation

DEFAULT_DISCLAIMER = u'''The EDRN is involved in researching hundreds of biomarkers. The following is a partial list of biomarkers and associated results that are currently available for access and viewing. The bioinformatics team at EDRN is currently working with EDRN collaborative groups to capture, curate, review, and post the results as it is available. EDRN also provides secure access to additional biomarker information not available to the public that is currently under review by EDRN research groups. If you have access to this information, please ensure that you are logged in. If you are unsure or would like access, please <a href='/contact-info'>contact the operator</a> for more information.'''

def _getPortal(context):
    return getToolByName(context, 'portal_url').getPortalObject()


def nullUpgradeStep(setupTool):
    '''A null step for when a profile upgrade requires no custom activity.'''


def upgradeBiomarkerFolders(setupTool):
    '''Set up faceted navigation and add disclaimers on all Biomarker Folders.'''
    portal = _getPortal(setupTool)
    request = portal.REQUEST
    catalog = getToolByName(portal, 'portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=IBiomarkerFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the common situation is that our EDRN
        # public portal does indeed have at least one Biomarker Folder
        if 'biomarkers' in portal.keys():
            results = [portal['biomarkers']]
    for folder in results:
        setFacetedNavigation(folder, request, force=True)
        folder.disclaimer = DEFAULT_DISCLAIMER


def loadPortalTypes(setupTool):
    setupTool.runImportStepFromProfile(PROFILE_ID, 'typeinfo')

