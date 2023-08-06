# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''
EKE Publications: RDF ingest for publication folders and their publications.
'''

from eke.knowledge.browser.rdf import CreatedObject, KnowledgeFolderIngestor
from rdflib import URIRef, ConjunctiveGraph, URLInputSource
from Acquisition import aq_inner
from eke.publications.interfaces import IPublication
from eke.publications import ENTREZ_TOOL, ENTREZ_EMAIL
from plone.i18n.normalizer.interfaces import IIDNormalizer
from Bio import Entrez
from zope.component import getUtility
import plone.api, contextlib, logging, cgi

_logger = logging.getLogger(__name__)

# Constants
FETCH_GROUP_SIZE = 450 # Fetch this many publications in Entrez.fetch, pausing to construct objects between each

# Other constnats: Well-known URI refs
_publicationTypeURI = URIRef('http://edrn.nci.nih.gov/rdf/types.rdf#Publication')
_typeURI            = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
_pmidURI            = URIRef('http://edrn.nci.nih.gov/rdf/schema.rdf#pmid')

# Set up Entrez
Entrez.tool = ENTREZ_TOOL
Entrez.email = ENTREZ_EMAIL

class PublicationFolderIngestor(KnowledgeFolderIngestor):
    '''Publication folder ingestion.'''
    def addGraphToStatements(self, graph, statements):
        u'''Add the statements in the RDF ``graph`` to the ``statements`` dict.'''
        for s, p, o in graph:
            if s not in statements:
                statements[s] = {}
            predicates = statements[s]
            if p not in predicates:
                predicates[p] = []
            predicates[p].append(o)
    def getRDFStatements(self):
        u'''Parse the main and additional RDF data sources and return a dict {uri → {predicate → [objects]}}'''
        context = aq_inner(self.context)
        urls = [context.rdfDataSource]
        urls.extend(context.additionalDataSources)
        statements = {}
        for url in urls:
            graph = ConjunctiveGraph()
            graph.parse(URLInputSource(url))
            self.addGraphToStatements(graph, statements)
        return statements
    def getIdentifiersForPubMedID(self, statements):
        u'''Given statements in the form of a dict {uri → {predicate → [objects]}}, yield a new dict
        {uri → PubMedID} including only those uris that are EDRN publication objects and only including
        those that have PubMedIDs.  In addition, don't duplicate PubMedIDs.'''
        identifiers, pubMedIDs = {}, set()
        for uri, predicates in statements.iteritems():
            uri = unicode(uri)
            typeURI = predicates[_typeURI][0]
            if typeURI != _publicationTypeURI: continue
            if _pmidURI not in predicates: continue
            pmID = predicates[_pmidURI][0]
            pmID = unicode(pmID).strip()
            if not pmID: continue
            if pmID == u'N/A': continue
            if pmID in pubMedIDs:
                _logger.warning('PubMedID %s duplicated in %s, ignoring that URI', pmID, uri)
                continue
            identifiers[uri] = pmID
            pubMedIDs.add(pmID)
        return identifiers
    def filterExistingPublications(self, identifiers):
        u'''Given a dict {uri → PubMedID} return a dict {uri → PubMedID} includes only those for
        which an existing Publication with the given uri identifier does not yet exist.'''
        catalog = plone.api.portal.get_tool('portal_catalog')
        found = catalog(identifier=identifiers.keys(), object_provides=IPublication.__identifier__)
        for f in found:
            del identifiers[f.identifier]
        return identifiers
    def divvy(self, identifiers):
        identifiers = identifiers.items()
        while len(identifiers) > 0:
            group = identifiers[:FETCH_GROUP_SIZE]
            identifiers = identifiers[FETCH_GROUP_SIZE:]
            yield group
    def getTitle(self, medline):
        u'''Extract the title from a medline record'''
        return unicode(medline[u'MedlineCitation'][u'Article'][u'ArticleTitle'])
    def setAuthors(self, pub, medline):
        u'''Set up the authors of a ``pub`` given its ``medline`` record.'''
        authorList = medline[u'MedlineCitation'][u'Article'].get(u'AuthorList', [])
        names = []
        for author in authorList:
            lastName = author.get(u'LastName', None)
            if not lastName:
                initials = author.get(u'Initials', None)
                if not initials: continue
            initials = author.get(u'Initials', None)
            name = u'{} {}'.format(lastName, initials) if initials else lastName
            names.append(name)
        pub.authors = names
    def createMissingPublications(self, identifiers):
        u'''Given a dict {uri → PubMedID}, create Publications using data from PubMed.  Return a sequence
        of CreatedObjects.'''
        context = aq_inner(self.context)
        normalize = getUtility(IIDNormalizer).normalize
        createdObjects = []
        for group in self.divvy(identifiers):
            identifiers, pubMedIDs = [i[0] for i in group], [i[1] for i in group]
            _logger.warning(u'Fetching from Entrez %d PubMedIDs', len(pubMedIDs))
            with contextlib.closing(Entrez.efetch(db='pubmed',retmode='xml',rettype='medline',id=pubMedIDs)) as handle:
                records = Entrez.read(handle)
                for i in zip(identifiers, records):
                    identifier, medline = unicode(i[0]), i[1]
                    pubMedID = unicode(medline[u'MedlineCitation'][u'PMID'])
                    title = self.getTitle(medline)
                    objID = normalize(pubMedID + u' ' + title)
                    try:
                        pub = context[context.invokeFactory('Publication', objID)]
                    except:
                        _logger.warning('Publication %s already exists, skipping', objID)
                        continue
                    pub.identifier = identifier
                    pub.title = title
                    abstract = medline[u'MedlineCitation'][u'Article'].get(u'Abstract', None)
                    if abstract:
                        paragraphs = abstract.get(u'AbstractText', [])
                        if len(paragraphs) > 0:
                            pub.abstract = u'\n'.join([u'<p>{}</p>'.format(cgi.escape(j)) for j in paragraphs])
                    self.setAuthors(pub, medline)
                    issue = medline[u'MedlineCitation'][u'Article'][u'Journal'][u'JournalIssue'].get(u'Issue', None)
                    if issue: pub.issue = unicode(issue)
                    volume = medline[u'MedlineCitation'][u'Article'][u'Journal'][u'JournalIssue'].get(u'Volume', None)
                    if volume: pub.volume = unicode(volume)
                    pub.journal = unicode(medline[u'MedlineCitation'][u'Article'][u'Journal'][u'ISOAbbreviation'])
                    year = medline[u'MedlineCitation'][u'Article'][u'Journal'][u'JournalIssue'][u'PubDate'].get(
                        u'Year', None
                    )
                    if year: pub.year = unicode(year)
                    month = medline[u'MedlineCitation'][u'Article'][u'Journal'][u'JournalIssue'][u'PubDate'].get(
                        u'Month', None
                    )
                    if month: pub.month = unicode(month)
                    pub.pubMedID = pubMedID
                    pub.reindexObject()
                    createdObjects.append(CreatedObject(pub))
        return createdObjects
    def __call__(self):
        statements = self.getRDFStatements()
        identifiers = self.getIdentifiersForPubMedID(statements)
        missingIdentifiers = self.filterExistingPublications(identifiers)
        self.objects = self.createMissingPublications(missingIdentifiers)
        return self.renderResults()

        # rc = super(PublicationFolderIngestor, self).__call__()
        # createdObjects, renderMode = self.objects, self.render
        # self.render = False
        # for url in aq_inner(self.context).additionalDataSources:
        #     super(PublicationFolderIngestor, self).__call__(rdfDataSource=url)
        #     createdObjects.extend(self.objects)
        # self.objects, self.render = createdObjects, renderMode
        # return rc

# class PublicationHandler(IngestHandler):
#     '''Handler for ``Publication`` objects.'''
#     def createObjects(self, objectID, title, uri, predicates, statements, context):
#         pub = context[context.invokeFactory('Publication', objectID)]
#         updateObject(pub, uri, predicates)
#         return [CreatedObject(pub)]


