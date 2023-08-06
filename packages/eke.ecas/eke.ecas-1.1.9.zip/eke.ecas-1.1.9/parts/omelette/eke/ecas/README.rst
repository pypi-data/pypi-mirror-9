This package provides Plone 3 content objects for the EDRN Knowledge
Environment (EKE_)'s management, display, and RDF ingest of science data.


Content Types
=============

The content types introduced in this package include the following:

Dataset Folder
    A folder that contains Datasets.  It can also repopulate its
    contents from an RDF data source.
Dataset
    A single dataset identified by URI_.

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


Dataset Folder
~~~~~~~~~~~~~~

A Dataset Folder contains Datasets.  They can be created anywhere in the
portal::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='dataset-folder')
    >>> l.url.endswith('createObject?type_name=Dataset+Folder')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = u'Toenail Clippings'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/datasets/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'toenail-clippings' in portal.objectIds()
    True
    >>> f = portal['toenail-clippings']
    >>> f.title
    'Toenail Clippings'
    >>> f.description
    'This folder is just for functional tests.'
    >>> f.rdfDataSource
    'testscheme://localhost/datasets/a'

Dataset Folders hold Datasets as well as other Dataset Folders.  We'll test
adding Datasets below, but let's make sure there's a link to created nested
Dataset Folders::

    >>> browser.open(portalURL + '/toenail-clippings')
    >>> l = browser.getLink(id='dataset-folder')
    >>> l.url.endswith('createObject?type_name=Dataset+Folder')
    True


Dataset
~~~~~~~

A single Dataset object corresponds with a single dataset in ECAS.
Datasets can be created only in Dataset Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='dataset')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

However, before we create one, we'll need some sites, protocols, and body
systems also present in the portal, since Datasets refer to both kinds of
objects.  Let's add some sites::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='site-folder').click()
    >>> browser.getControl(name='title').value = 'Questionable Sites'
    >>> browser.getControl(name='description').value = 'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/sites/b'
    >>> browser.getControl(name='peopleDataSource').value = 'testscheme://localhost/people/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/questionable-sites/ingest')

And now some protocols::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='study-folder').click()
    >>> browser.getControl(name='title').value = 'Questionable Studies'
    >>> browser.getControl(name='description').value = 'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/protocols/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/questionable-studies/ingest')

And some body systems::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='knowledge-folder').click()
    >>> browser.getControl(name='title').value = u'My Private Parts'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/bodysystems/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/my-private-parts/ingest')

And finally, let's create one our very first Dataset::

    >>> browser.open(portalURL + '/toenail-clippings')
    >>> l = browser.getLink(id='dataset')
    >>> l.url.endswith('createObject?type_name=Dataset')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = 'Toenail Clipping Count 1'
    >>> browser.getControl(name='custodian').value = 'Robert Magnolia'
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='sites:list').displayValue = ["Dr Tongue's 3D Clinic"]
    >>> browser.getControl(name='authors:lines').value = 'Dr Tongue\nBob Magnolia'
    >>> browser.getControl(name='bodySystem:list').displayValue = ['Anus']
    >>> browser.getControl(name='grantSupport:lines').value = 'Very little.\nVery little indeed.'
    >>> browser.getControl(name='researchSupport:lines').value = 'Even less.\nEven less indeed.'
    >>> browser.getControl(name='dataDisclaimer').value = "Believe me, you don't want to get near these toenail clippings."
    >>> browser.getControl(name='studyBackground').value = 'Well, I noticed a large number of toenail clippings under my desk.'
    >>> browser.getControl(name='studyMethods').value = 'I bent down and started counting them.'
    >>> browser.getControl(name='studyResults').value = 'In any given week, I had about 12 to 16 toenail clippings.'
    >>> browser.getControl(name='studyConclusion').value = 'My toenails grow rather quickly.'
    >>> from datetime import datetime
    >>> today = datetime.now()
    >>> browser.getControl(name='dataUpdateDate_year').displayValue = [str(today.year)]
    >>> browser.getControl(name='dataUpdateDate_month').value = ['%02d' % today.month]
    >>> browser.getControl(name='dataUpdateDate_day').value  = ['%02d' % today.day]
    >>> browser.getControl(name='identifier').value = 'http://questionablescience.com/toenails/1'
    >>> browser.getControl(name='collaborativeGroup').value = 'Kooks R Us'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink(id='workflow-transition-publish').click()
    >>> 'toenail-clipping-count-1' in f.objectIds()
    True
    >>> d = f['toenail-clipping-count-1']
    >>> d.title
    'Toenail Clipping Count 1'
    >>> d.custodian
    'Robert Magnolia'
    >>> d.protocol.title
    'Public Safety'
    >>> d.sites[0].title
    u"Dr Tongue's 3D Clinic"
    >>> d.authors
    ('Dr Tongue', 'Bob Magnolia')
    >>> d.bodySystem.title
    'Anus'
    >>> d.grantSupport
    ('Very little.', 'Very little indeed.')
    >>> d.researchSupport
    ('Even less.', 'Even less indeed.')
    >>> d.dataDisclaimer
    "Believe me, you don't want to get near these toenail clippings."
    >>> d.studyBackground
    'Well, I noticed a large number of toenail clippings under my desk.'
    >>> d.studyMethods
    'I bent down and started counting them.'
    >>> d.studyResults
    'In any given week, I had about 12 to 16 toenail clippings.'
    >>> d.studyConclusion
    'My toenails grow rather quickly.'
    >>> d.dataUpdateDate.year == today.year, d.dataUpdateDate.month == today.month, d.dataUpdateDate.day == today.day
    (True, True, True)
    >>> d.collaborativeGroup
    'Kooks R Us'
    >>> d.bodySystemName
    'Anus'
    >>> d.protocolName
    'Public Safety'


Dataset View
~~~~~~~~~~~~

The default view for a Dataset is fairly basic.  However, the identifier
(which is a URL) should be hyperlinked::

    >>> browser.open(portalURL + '/toenail-clippings/toenail-clipping-count-1')
    >>> browser.contents
    '...href="http://questionablescience.com/toenails/1"...'


Dataset Folder View
~~~~~~~~~~~~~~~~~~~

A Dataset Folder by default displays its datasets in alphabetical order by
title.  Let's check that.  First, we'll need to toss in a couple other
datasets::

    >>> browser.open(portalURL + '/toenail-clippings')
    >>> browser.getLink(id='dataset').click()
    >>> browser.getControl(name='title').value = 'Toenail Clipping Count 2'
    >>> browser.getControl(name='identifier').value = 'http://questionablescience.com/toenails/2'
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink(id='workflow-transition-publish').click()

That's one; now another::

    >>> browser.open(portalURL + '/toenail-clippings')
    >>> browser.getLink(id='dataset').click()
    >>> browser.getControl(name='title').value = 'Toenail Clipping Count 3'
    >>> browser.getControl(name='identifier').value = 'http://questionablescience.com/toenails/3'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink(id='workflow-transition-publish').click()

The alert reader will notice that Toenail Clipping Count 3 didn't have a
protocol associated with it; that's intentional.  You'll see why; but first,
let's checking the ordering::

    >>> browser.open(portalURL + '/toenail-clippings')
    >>> browser.contents
    '...Toenail Clipping Count 1...Toenail Clipping Count 2...'

Perfect.  Of course, the user can sort by clicking on the column headings.
Did Toenail Clipping Count 3 didn't get shown?  Double-check::

    >>> 'Toenail Clipping Count 3' not in browser.contents
    True

Good!  That's because CA-576 says that datasets without associated protocols
shouldn't be shown.  Now you see why we created that dataset *without* a
protocol!

http://oodt.jpl.nasa.gov/jira/browse/CA-406 says we need to see organ name,
protocol name, and collaborative group in the list.  Do we?  Let's find out::

    >>> browser.contents
    '...Toenail Clipping Count 1...Alottaspank, Dirk...Anus...Public Safety...Kooks R Us...'

Additionally, any nested Dataset Folders should appear above the dataset
list::

    >>> 'Special Subsection' not in browser.contents
    True
    >>> browser.getLink(id='dataset-folder').click()
    >>> browser.getControl(name='title').value = 'Special Subsection on Pinky Toe Clipping Isolation'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/toenail-clippings')
    >>> browser.contents
    '...Special Subsection...Toenail Clipping Count 1...Toenail Clipping Count 2...'

Issue http://oodt.jpl.nasa.gov/jira/browse/CA-463 says that "Body System" is
wrong and "Organ" is correct.  Checking::

    >>> browser.contents
    '...Title...PI(s)...Organ...Protocol...Collaborative Group...'
    >>> 'Body System' not in browser.contents
    True

And issue CA-501 says we need a disclaimer on the dataset list.  Is
it there?  Let's find out::

    >>> browser.contents
    '...The EDRN is involved in researching hundreds of biomarkers.  The following is a partial list...'
    
No problem.  Issue CA-513 wants protocols to be hyperlinks to their
protocols::

    >>> browser.contents
    '...<a href="http://nohost/questionable-studies/ps-public-safety">Public Safety</a>...'

Lookin' good.  The issue also wanted collaborative groups to be hyperlinks to
their group descriptions.  I think it'd be better to link them to their
Collaborative Group objects.  But we can't test for that here (dependency
loop), so check the ``edrnsite.collaborations`` package to see that in action.


RDF Ingestion
-------------

Dataset Folders support a URL-callable method that causes them to ingest
content via RDF, just like Knowledge Folders in the ``eke.knowledge`` package.

First, let's create a new, empty folder with which to play::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='dataset-folder').click()
    >>> browser.getControl(name='title').value = 'Waxy Buildup'
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/datasets/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/waxy-buildup/content_status_modify?workflow_action=publish')
    >>> f = portal['waxy-buildup']

Ingesting from the RDF data source ``testscheme://localhost/datasets/a``::

    >>> browser.open(portalURL + '/waxy-buildup/ingest')
    >>> browser.contents
    '...The following items have been created...Get Bent...'
    >>> f.objectIds()
    ['get-bent']
    >>> d = f['get-bent']
    >>> d.title
    'Get Bent'
    >>> d.custodian
    'Joe McBlow <joe@mcblow.com>'
    >>> d.protocol.title
    'Public Safety'
    >>> d.sites[0].title
    u"Dr Tongue's 3D Clinic"
    >>> d.authors
    ('Jim Blow',)
    >>> 'REDACTED-1' in d.grantSupport
    True
    >>> 'REDACTED-2' in d.grantSupport
    True
    >>> len(d.grantSupport)
    2
    >>> 'Blow Me Extramural' in d.researchSupport
    True
    >>> 'Blow You Intramural' in d.researchSupport
    True
    >>> len(d.researchSupport)
    2
    >>> d.dataDisclaimer
    "If you share this I'll kill you."
    >>> d.studyBackground
    'You must have a death wish.'
    >>> d.studyMethods
    'None of your business.'
    >>> d.studyResults
    'Nice try, bub.'
    >>> d.studyConclusion
    'Classified.'
    >>> d.dataUpdateDate.year, d.dataUpdateDate.month, d.dataUpdateDate.day
    (2009, 12, 24)
    >>> d.collaborativeGroup
    'NSA'
    >>> d.bodySystem.title
    'Anus'
    >>> d.bodySystemName
    'Anus'
    >>> d.protocolName
    'Public Safety'
    >>> d.identifier
    'urn:edrn:top-secret-data'

The source ``testscheme://localhost/datasets/b`` contains both the above
Dataset and an additional one.  Since ingestion purges existing objects, we
shouldn't get duplicate copies of the above Dataset::

    >>> browser.getLink('Edit').click()
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/datasets/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> objIDs = f.objectIds()
    >>> objIDs.sort()
    >>> objIDs
    ['chad-vader', 'get-bent', 'get-not-as-bent']


Protocol Associations
~~~~~~~~~~~~~~~~~~~~~

http://oodt.jpl.nasa.gov/jira/browse/CA-425 noted that protocols should link
to datasets (as well as to biomarkers).  Protocol information in the protocol
RDF doesn't explicitly give such associations, however the RDF from datasets
does.

Does such ingest link a dataset to a biomarker?  Let's find out::

    >>> browser.open(portalURL + '/questionable-studies/ps-public-safety')
    >>> browser.contents
    '...Public Safety...Datasets...Get Bent...'


Searching for Datasets
~~~~~~~~~~~~~~~~~~~~~~

Issue http://oodt.jpl.nasa.gov/jira/browse/CA-512 takes to task several ways
that searches happen for eCAS datasets.  First off, it claims that searching
by the PI name doesn't yield a matching dataset.  I certainly beg to differ::

    >>> from Products.CMFCore.utils import getToolByName
    >>> catalog = getToolByName(portal, 'portal_catalog')
    >>> results = catalog.unrestrictedSearchResults(SearchableText='Alottaspank')
    >>> titles = [i.Title for i in results if i.portal_type == 'Dataset']
    >>> titles.sort()
    >>> titles
    ['Chad Vader', 'Get Bent', 'Get not as bent', 'Toenail Clipping Count 1', 'Toenail Clipping Count 2']

See?  That works.  It also has the outlandish idea that searching on a
descriptive attribute of the dataset does not match any dataset.  To
demonstrate a descriptive attribute, it mentions a specific protocol name.
Well, take a look at this::

    >>> results = catalog.unrestrictedSearchResults(SearchableText='Public Safety')
    >>> titles = [i.Title for i in results if i.portal_type == 'Dataset']
    >>> titles.sort()
    >>> titles
    ['Chad Vader', 'Get Bent', 'Get not as bent', 'Toenail Clipping Count 1', 'Toenail Clipping Count 2']

It also draws the absolutely unfounded conclusion that you can't search by
collaborative group.  To that, I exhibit the following::

    >>> results = catalog.unrestrictedSearchResults(SearchableText='NSA')
    >>> [i.Title for i in results if i.portal_type == 'Dataset']
    ['Get Bent']

Good day, sir!  I said, "Good day!"


Yet More Searching Woes
'''''''''''''''''''''''

Issue http://oodt.jpl.nasa.gov/jira//browse/CA-523 says that searching by a
dataset name should also match protocols that are using that dataset.  Let's
find out::

    >>> results = catalog.unrestrictedSearchResults(SearchableText='Get Bent')
    >>> titles = [i.Title for i in results if i.portal_type == 'Protocol']
    >>> titles.sort()
    >>> titles
    ['Public Safety']

Works as intended.


Security
~~~~~~~~

Datasets from eCAS contain sensitive information that we can't have the
general public looking at until the quality control status of the datasets say
they're ready to go.  But that's entirely in the purview of ECAS.  All the
portal has to do is provide links into ECAS.  However, information provided by
ECAS's RDF into the portal shouldn't be visible unless that data is supposed
to be visible.

To demonstrate this capability, let's revisit the "Get Bent" dataset and note
its visibility::

    >>> browser.open(portalURL + '/waxy-buildup/get-bent')
    >>> browser.contents
    '...State:...Published...'

The "Get not as bent" dataset is still under review, so it should be private,
however in the plone.app.testing framework we don't have access to the snazzy
workflows, so chances are it'll be in the public draft state::

    >>> browser.open(portalURL + '/waxy-buildup/get-not-as-bent')
    >>> browser.contents
    '...State:...Public draft...'
    
However, this dataset does allow those members of the "silly-group" to view
it::

    >>> browser.open(portalURL + '/waxy-buildup/get-not-as-bent/@@sharing')
    >>> browser.contents
    '...Name...ldap://edrn/groups/silly-group...'

Finally, there's a dataset that doesn't even have a QA state, so by default,
it should be private (again, non-snazzy workflows notwithstanding)::

    >>> browser.open(portalURL + '/waxy-buildup/chad-vader')
    >>> browser.contents
    '...State:...Public draft...'

All of this came about due to http://oodt.jpl.nasa.gov/jira/browse/CA-475.

CA-654 wanted the lock icons to go away::

    >>> browser.open(portalURL + '/waxy-buildup')
    >>> 'Unreleased dataset' in browser.contents
    False
    >>> 'lock_icon' in browser.contents
    False

Similarly, the note about having to be logged in should be gone::

    >>> 'indicates content for which you must be logged in' in browser.contents
    False

Great.


RDF Data Sources
~~~~~~~~~~~~~~~~

The URL to an RDF data source is nominally displayed on an ECAS folder, but
only if you're an administrator::

    >>> browser.open(portalURL + '/waxy-buildup')
    >>> browser.contents
    '...RDF Data Source...testscheme://localhost/datasets/b...'

However, mere mortals shouldn't see that::

    >>> unprivilegedBrowser.open(portalURL + '/waxy-buildup')
    >>> 'RDF Data Source' not in unprivilegedBrowser.contents
    True

That's it!


.. References:
.. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. _RDF: http://w3.org/RDF/
.. _URI: http://w3.org/Addressing/
