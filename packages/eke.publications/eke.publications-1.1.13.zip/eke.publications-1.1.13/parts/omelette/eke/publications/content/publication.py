# encoding: utf-8
# Copyright 2009-2011 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''Publication.'''

from eke.knowledge import dublincore
from eke.knowledge.content import knowledgeobject
from eke.publications import ProjectMessageFactory as _
from eke.publications.config import PROJECTNAME
from eke.publications.interfaces import IPublication
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.CMFCore.utils import getToolByName
from zope.interface import implements, directlyProvides
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary

PublicationSchema = knowledgeobject.KnowledgeObjectSchema.copy() + atapi.Schema((
    atapi.StringField(
        'abstract',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Abstract'),
            description=_(u'Formal scientific abstract of the publication.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/rdf/schema.rdf#abstract',
    ),
    atapi.LinesField(
        'authors',
        required=False,
        storage=atapi.AnnotationStorage(),
        multiValued=True,
        searchable=True,
        widget=atapi.LinesWidget(
            label=_(u'Authors'),
            description=_(u'Names of authors who wrote the publication.'),
        ),
        predicateURI=dublincore.AUTHOR_URI,
    ),
    atapi.StringField(
        'issue',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Issue'),
            description=_(u'In what issue the publication appeared.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/rdf/schema.rdf#issue',
    ),
    atapi.StringField(
        'volume',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Volume'),
            description=_(u'In what volume the issue appeared in which the publication appeared.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/rdf/schema.rdf#volume',
    ),
    atapi.StringField(
        'journal',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Journal'),
            description=_(u'Name of the journal in which the publication appeared.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/rdf/schema.rdf#journal',
    ),
    atapi.StringField(
        'pubMedID',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'PubMed ID'),
            description=_(u'PubMed identifier for the publication.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/rdf/schema.rdf#pmid',
    ),
    atapi.StringField(
        'year',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Year'),
            description=_(u'Year of publication.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/rdf/schema.rdf#year',
    ),
    atapi.StringField(
        'month',
        required=False,
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u'Month'),
            description=_(u'Month of publication.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/rdf/schema.rdf#month',
    ),
    atapi.StringField(
        'pubURL',
        required=False,
        storage=atapi.AnnotationStorage(),
        validators=('isURL',),
        widget=atapi.StringWidget(
            label=_(u'URL'),
            description=_(u'Location of the publication.'),
        ),
        predicateURI=u'http://edrn.nci.nih.gov/rdf/schema.rdf#pubURL',
    ),
))
# FIXME: KnowledgeObjectSchema has title's predicate set to something wrong.
# When that's finally fixed, remove this line:
PublicationSchema['title'].predicateURI = dublincore.TITLE_URI

finalizeATCTSchema(PublicationSchema, folderish=False, moveDiscussion=False)

class Publication(knowledgeobject.KnowledgeObject):
    '''Publication.'''
    implements(IPublication)
    schema      = PublicationSchema
    portal_type = 'Publication'
    abstract    = atapi.ATFieldProperty('abstract')
    authors     = atapi.ATFieldProperty('authors')
    issue       = atapi.ATFieldProperty('issue')
    volume      = atapi.ATFieldProperty('volume')
    journal     = atapi.ATFieldProperty('journal')
    pubMedID    = atapi.ATFieldProperty('pubMedID')
    year        = atapi.ATFieldProperty('year')
    month       = atapi.ATFieldProperty('month')
    pubURL      = atapi.ATFieldProperty('pubURL')
    
atapi.registerType(Publication, PROJECTNAME)

def PublicationVocabularyFactory(context):
    catalog = getToolByName(context, 'portal_catalog')
    # TODO: filter by review_state?
    results = catalog(object_provides=IPublication.__identifier__, sort_on='sortable_title')
    return SimpleVocabulary([SimpleVocabulary.createTerm(i.UID, i.UID, i.Title.decode('utf-8')) for i in results])
directlyProvides(PublicationVocabularyFactory, IVocabularyFactory)

