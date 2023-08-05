# encoding: utf-8
# Copyright 2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eke.publications.interfaces import IPublication
from Products.CMFPlone.Portal import PloneSite
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName


class _Extra(object):
    def __init__(self, doc_attr, index_type, lexicon_id):
        self.doc_attr, self.index_type, self.lexicon_id = doc_attr, index_type, lexicon_id

def setFacetedNavigation(folder, request):
    subtyper = getMultiAdapter((folder, request), name=u'faceted_subtyper')
    if subtyper.is_faceted or not subtyper.can_enable: return
    subtyper.enable()
    criteria = ICriteria(folder)
    for cid in criteria.keys():
        criteria.delete(cid)
    criteria.add('resultsperpage', 'bottom', 'default', title='Results per page', hidden=True, start=0, end=50, step=5,
        default=20)
    criteria.add(
        'checkbox', 'bottom', 'default',
        title='Obj provides',
        hidden=True,
        index='object_provides',
        operator='or',
        vocabulary=u'eea.faceted.vocabularies.ObjectProvides',
        default=[IPublication.__identifier__],
        count=False,
        maxitems=0,
        sortreversed=False,
        hidezerocount=False
    )
    criteria.add('debug', 'top', 'default', title='Debug Criteria', user='kelly')
    criteria.add('text', 'top', 'default', title=u'Search', hidden=False, index='SearchableText',
        count=False, onlyallelements=True)    
    criteria.add('text', 'top', 'advanced', title=u'Search Titles Only', hidden=False, index='Title', count=False,
        onlyallelements=True)
    criteria.add('text', 'top', 'advanced', title=u'Authors', hidden=False, index='authors', count=False,
        onlyallelements=True)
    criteria.add('text', 'top', 'advanced', title=u'Journal', hidden=False, index='journal', count=False,
        onlyallelements=True)
    criteria.add('text', 'top', 'advanced', title=u'Abstract', hidden=False, index='abstract', count=False,
        onlyallelements=True)
    criteria.add('sorting', 'bottom', 'default', title=u'Sort on', hidden=False, default='year(reverse)')
    IFacetedLayout(folder).update_layout('faceted_publications_view')
    # To make the text field work, the authors index needs to be a text index
    catalog = getToolByName(folder, 'portal_catalog')
    found = False
    for index in catalog.getIndexObjects():
        if index.id == 'authors':
            found = True
            if index.meta_type == 'ZCTextIndex': return
    if found:
        catalog.delIndex('authors')
    catalog.addIndex('authors', 'ZCTextIndex', _Extra('authors', 'Okapi BM25 Rank', 'plaintext_lexicon'))
    catalog.reindexIndex('authors', request)
