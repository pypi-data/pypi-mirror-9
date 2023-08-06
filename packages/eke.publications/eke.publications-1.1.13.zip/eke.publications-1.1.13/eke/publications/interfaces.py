# encoding: utf-8
# Copyright 2009 California Institute of Technology. ALL RIGHTS
# RESERVED. U.S. Government Sponsorship acknowledged.

'''EKE Publications: interfaces.
'''

from zope import schema
from zope.container.constraints import contains
from eke.publications import ProjectMessageFactory as _
from eke.knowledge.interfaces import IKnowledgeFolder, IKnowledgeObject

class IPublicationFolder(IKnowledgeFolder):
    '''Publication folder.'''
    contains('eke.publications.interfaces.IPublication')
    additionalDataSources = schema.List(
        title=_(u'Additonal Data Sources'),
        description=_(u'URLs to additional sources of RDF that describe publications.'),
        required=False,
        value_type=schema.TextLine(
            title=_(u'Additonal Data Source'),
            description=_(u'URL to an additional source of RDF publication data.'),
        ),
    )

class IPublication(IKnowledgeObject):
    '''Publication.'''
    abstract = schema.Text(
        title=_(u'Abstract'),
        description=_(u'Formal scientific abstract of the publication.'),
        required=False,
    )
    authors = schema.List(
        title=_(u'Authors'),
        description=_(u'Names of authors who wrote the publication.'),
        required=False,
        value_type=schema.TextLine(title=_(u'Author Name'), description=_(u'Full name of the author, if available.')),
        unique=True,
    )
    issue = schema.TextLine(
        title=_(u'Issue'),
        description=_(u'In what issue the publication appeared.'),
        required=False,
    )
    volume = schema.TextLine(
        title=_(u'Volume'),
        description=_(u'In what volume the issue appeared in which the publication appeared.'),
        required=False,
    )
    journal = schema.TextLine(
        title=_(u'Journal'),
        description=_(u'Name of the journal in which the publication appeared.'),
        required=False,
    )
    pubMedID = schema.TextLine(
        title=_(u'PubMed ID'),
        description=_(u'PubMed identifier for the publication.'),
        required=False,
    )
    month = schema.TextLine(
        title=_(u'Month'),
        description=_(u'Month of publication.'),
        required=False,
    )
    year = schema.TextLine(
        title=_(u'Year'),
        description=_(u'Year of publication.'),
        required=False,
    )
    pubURL = schema.TextLine(
        title=_(u'URL'),
        description=_(u'Location of the publication.'),
        required=False,
    )
    