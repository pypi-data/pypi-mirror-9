This package provides Plone 3 content objects for the EDRN Knowledge
Environment (EKE_)'s management, display, and RDF ingest of publication data.


Content Types
=============

The content types introduced in this package include the following:

Publication Folder
    A folder that contains Publications.  It can also repopulate its
    contents from an RDF data source.
Publication
    A single publication identified by URI_.

The remainder of this document demonstrates the content types and RDF ingest
using a series of functional tests.


Tests
=====

First we have to set up some things and login to the site::

    >>> app = layer['app']
    >>> from plone.testing.z2 import Browser
    >>> from plone.app.testing import SITE_OWNER_NAME, SITE_OWNER_PASSWORD
    >>> browser = Browser(app)
    >>> browser.handleErrors = False
    >>> browser.addHeader('Authorization', 'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
    >>> portal = layer['portal']    
    >>> portalURL = portal.absolute_url()

We'll also have a second browser that's unprivileged for some later
demonstrations::

    >>> unprivilegedBrowser = Browser(app)

Now we can check out the new types introduced in this package.


Addable Content
---------------

Here we'll exercise some of the content objects available in this project and
demonstrate their properties and constraints.


Publication Folder
~~~~~~~~~~~~~~~~~~

A publication folder contains publications.  They can be created anywhere
in the portal::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='publication-folder')
    >>> l.url.endswith('createObject?type_name=Publication+Folder')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'My Magazine Collection'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/pubs/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'my-magazine-collection' in portal.objectIds()
    True
    >>> f = portal['my-magazine-collection']
    >>> f.title
    'My Magazine Collection'
    >>> f.description
    'This folder is just for functional tests.'
    >>> f.rdfDataSource
    'testscheme://localhost/pubs/a'

Publication folders hold Publications as well as other Publication Folders.
We'll test adding Publications below, but let's make sure there's a link to
created nested Publication Folders::

    >>> browser.open(portalURL + '/my-magazine-collection')
    >>> l = browser.getLink(id='publication-folder')
    >>> l.url.endswith('createObject?type_name=Publication+Folder')
    True


Publication
~~~~~~~~~~~

A single Publication object corresponds with a single real-world publication.
In EDRN, all publications are assumed to be published in a journal—even
standalone books.  Unfortunate, but there we are.  Anyway, Publications can be
created on in Publication Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='publication')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So, let's create one in our above Publication Folder::

    >>> browser.open(portalURL + '/my-magazine-collection')
    >>> l = browser.getLink(id='publication')
    >>> l.url.endswith('createObject?type_name=Publication')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'S.W.I.T.C.H.: a new model for release of norepinephrine'
    >>> browser.getControl(name='description').value = 'Repeated use of our S.W.I.T.C.H. model have shown high success.'
    >>> browser.getControl(name='abstract').value = 'The model produced enormous levels of norepinephrine.'
    >>> browser.getControl(name='authors:lines').value = u'Faetishe, JM\nDivine, HR'
    >>> browser.getControl(name='identifier').value = 'http://unknown.com/pub13792'
    >>> browser.getControl(name='year').value = '1964'
    >>> browser.getControl(name='journal').value = 'Roue'
    >>> browser.getControl(name='issue').value = '3'
    >>> browser.getControl(name='volume').value = '4'
    >>> browser.getControl(name='pubMedID').value = '1645221Q'
    >>> browser.getControl(name='pubURL').value = 'http://unknown.com/printable/pub13792'
    >>> browser.getControl(name='form.button.save').click()
    >>> 's-w-i-t-c-h-a-new-model-for-release-of-norepinephrine' in f.objectIds()
    True
    >>> pub = f['s-w-i-t-c-h-a-new-model-for-release-of-norepinephrine']
    >>> pub.title
    'S.W.I.T.C.H.: a new model for release of norepinephrine'
    >>> pub.description
    'Repeated use of our S.W.I.T.C.H. model have shown high success.'
    >>> pub.abstract
    'The model produced enormous levels of norepinephrine.'
    >>> pub.authors
    ('Faetishe, JM', 'Divine, HR')
    >>> pub.identifier
    'http://unknown.com/pub13792'
    >>> pub.year
    '1964'
    >>> pub.journal
    'Roue'
    >>> pub.issue
    '3'
    >>> pub.volume
    '4'
    >>> pub.pubMedID
    '1645221Q'
    >>> pub.pubURL
    'http://unknown.com/printable/pub13792'
    
A publication page should include a link to its PubMed entry::

    >>> browser.contents
    '...<a href="http://www.ncbi.nlm.nih.gov/sites/entrez?Db=pubmed&amp;Cmd=DetailsSearch&amp;Term=1645221Q%5Buid%5D"...'

Lookin' good.


RDF Ingestion
-------------

Publication folders support a URL-callable method that causes them to ingest
content via RDF, just like Knowledge Folders in the ``eke.knowledge`` package.

First, let's create a new, empty folder with which to play::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='publication-folder').click()
    >>> browser.getControl(name='title').value = "Cook's Bookshelf"
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/pubs/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/cooks-bookshelf/content_status_modify?workflow_action=publish')
    >>> f = portal['cooks-bookshelf']

Ingesting from the RDF data source ``testscheme://localhost/pubs/a``::

    >>> browser.open(portalURL + '/cooks-bookshelf/ingest')
    >>> browser.contents
    '...The following items have been created...Early detection biomarkers for ovarian cancer...'
    >>> f.objectIds()
    ['23319948-early-detection-biomarkers-for-ovarian']
    >>> pub = f['23319948-early-detection-biomarkers-for-ovarian']
    >>> pub.title
    'Early detection biomarkers for ovarian cancer.'
    >>> pub.abstract
    '<p>Despite the widespread use of conventional and contemporary methods...'
    >>> pub.authors
    ('Sarojini S', 'Tamir A', 'Lim H', 'Li S', 'Zhang S', 'Goy A', 'Pecora A', 'Suh KS')
    >>> pub.identifier
    'http://is.gd/pVKq'
    >>> pub.year
    '2012'
    >>> pub.journal
    'J Oncol'
    >>> pub.issue
    ''
    >>> pub.volume
    '2012'
    >>> pub.pubMedID
    '23319948'


The source ``testscheme://localhost/pub/b`` contains both the above article and
a second one; however we shouldn't get duplicates::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/pubs/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> objIDs = f.objectIds()
    >>> objIDs.sort()
    >>> objIDs
    ['21666252-letter-to-the-editor-seqxml-and-orthoxml', '23319948-early-detection-biomarkers-for-ovarian']


Multiple Data Sources
~~~~~~~~~~~~~~~~~~~~~

As we'e seen, publication folders have a main RDF data source.  But they also
support zero or more additional sources of data.  Let's toss some of this
additional data in and see it can successfully ingest it::

	>>> browser.getLink('Edit').click()
	>>> browser.getControl(name='additionalDataSources:lines').value = 'testscheme://localhost/pubs/c\ntestscheme://localhost/pubs/d'
	>>> browser.getControl(name='form.button.save').click()
	>>> browser.getLink('Ingest').click()
	>>> len(f.objectIds())
	6
	

Vocabularies
------------

This package provides one vocabulary: a vocabulary of existing publications.
Here's what you get::

    >>> from zope.schema.interfaces import IVocabularyFactory
    >>> from zope.component import getUtility
    >>> v = getUtility(IVocabularyFactory, name='eke.publications.PublicationsVocabulary')
    >>> type(v(portal))
    <class 'zope.schema.vocabulary.SimpleVocabulary'>


Searching
---------

Issue http://oodt.jpl.nasa.gov/jira/browse/CA-514 says searching by author
name doesn't work.  Let's find out::

    >>> from Products.CMFCore.utils import getToolByName
    >>> catalog = getToolByName(portal, 'portal_catalog')
    >>> results = catalog.unrestrictedSearchResults(SearchableText='Sarojini')
	>>> [i.Title for i in results if i.portal_type == 'Publication']
	['Early detection biomarkers for ovarian cancer.']

Works!


.. References:
.. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. _RDF: http://w3.org/RDF/
.. _URI: http://w3.org/Addressing/
