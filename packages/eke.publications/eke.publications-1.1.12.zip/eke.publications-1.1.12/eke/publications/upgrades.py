# encoding: utf-8
# Copyright 2011–2015 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eke.publications import PROFILE_ID
from eke.publications.interfaces import IPublicationFolder
from Products.CMFCore.utils import getToolByName
from utils import setFacetedNavigation
from zope.component import getMultiAdapter
import plone.api, logging

_logger = logging.getLogger(__name__)

def _getPortal(context):
    return getToolByName(context, 'portal_url').getPortalObject()

def nullUpgradeStep(setupTool):
    '''A null step for when a profile upgrade requires no custom activity.'''

def setUpFacetedNavigation(setupTool):
    '''Set up faceted navigation on all Publication Folders.'''
    portal = _getPortal(setupTool)
    request = portal.REQUEST
    catalog = getToolByName(portal, 'portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=IPublicationFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the common situation is that our EDRN
        # public portal does indeed have at least one Publication Folder
        if 'publications' in portal.keys():
            results = [portal['publications']]
    for pubFolder in results:
        setFacetedNavigation(pubFolder, request)

def runCatalogImportStep(setupTool):
    u'''(Re)Run the portal_catalog GenericSetup import step.'''
    setupTool.runImportStepFromProfile(PROFILE_ID, 'catalog')

def dropExistingPublications(setupTool):
    u'''Drop all existing publications so we can re-create them on the next RDF ingest
    with proper PubMed-provided metadata.'''
    catalog = plone.api.portal.get_tool('portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=IPublicationFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the common situation is that our EDRN
        # public portal does indeed have at least one Publication Folder
        portal = plone.api.portal.get()
        if 'publications' in portal.keys():
            results = [portal['publications']]
    for pubFolder in results:
        pubFolder.manage_delObjects(pubFolder.objectIds())

def rebuildPublicationFacets(setupTool):
    u'''Nuke the faceted settings and rebuild them on all publication folders.'''
    _logger.critical('@@@@ running catalog step')
    setupTool.runImportStepFromProfile(PROFILE_ID, 'catalog')
    _logger.critical('@@@@ running atcttool step')
    setupTool.runImportStepFromProfile(PROFILE_ID, 'atcttool')
    portal = _getPortal(setupTool)
    request = portal.REQUEST
    catalog = plone.api.portal.get_tool('portal_catalog')
    results = [i.getObject() for i in catalog(object_provides=IPublicationFolder.__identifier__)]
    if len(results) == 0:
        # wtf? catalog must be out of date, because the common situation is that our EDRN
        # public portal does indeed have at least one Publication Folder
        portal = plone.api.portal.get()
        if 'publications' in portal.keys():
            results = [portal['publications']]
    for pubFolder in results:
        subtyper = getMultiAdapter((pubFolder, request), name=u'faceted_subtyper')
        subtyper.disable()
        _logger.critical('@@@@ setting up facets on %s', '/'.join(pubFolder.getPhysicalPath()))
        setFacetedNavigation(pubFolder, request)
