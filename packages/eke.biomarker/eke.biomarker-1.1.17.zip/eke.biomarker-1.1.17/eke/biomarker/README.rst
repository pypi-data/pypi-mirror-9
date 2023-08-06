This package provides Plone 3 content objects for the EDRN Knowledge
Environment (EKE_)'s management, display, and RDF ingest of biomarkers and
related information.  A biomarker is a chemical indicator for disease.  This
component, ``eke.biomarker``, provides search, display, and RDF ingest of
protocol information.


Content Types
=============

The content types introduced in this package include the following:

Biomarker Folder
    A folder that contains biomarkers and may be populated from an RDF data
    source.  It may also contain Biomarker Folders as sub-folders.
Elemental Biomarker
    A single biomarker carried out by EDRN and identified by URI_.
Biomarker Panel
    A collection of elemental biomarkers or other panels that, itself, behaves
    as a single biomarker.
Biomarker Body System
    Indications of a biomarker for a specific body system.
Body System Study
    Information from a study as it pertains to a biomarker's indications on a
    specific body system.
Study Statistics
    Statistical information from a study on a body system when indicated by a
    biomarker.
Review Listing
    A set of biomarkers selected for review by a review group.

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

We'll need a test group that we'll use later on in order to demonstrate
biomarker security::

    >>> from Products.CMFCore.utils import getToolByName
    >>> gtool = getToolByName(portal, 'portal_groups')
    >>> gtool.addGroup('ldap://edrn/groups/g1')
    True

Now we can check out the new types introduced in this package.


Addable Content
---------------

Here we'll exercise some of the content objects available in this project and
demonstrate their properties and constraints.


Biomarker Folder
~~~~~~~~~~~~~~~~

A biomarker folder contains biomarkers and other Biomarker Folders.  They can
be created anywhere in the portal::

    >>> browser.open(portalURL)
    >>> l = browser.getLink(id='biomarker-folder')
    >>> l.url.endswith('createObject?type_name=Biomarker+Folder')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = 'Questionable Biomarkers'
    >>> browser.getControl(name='description').value = 'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/biomarkers/a'
    >>> browser.getControl(name='bmoDataSource').value = 'testscheme://localhost/biomarkerorgans/a'
    >>> browser.getControl(name='disclaimer').value = u'You are legally obligated to not use these biomarkers.'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'questionable-biomarkers' in portal.objectIds()
    True
    >>> f = portal['questionable-biomarkers']
    >>> f.title
    'Questionable Biomarkers'
    >>> f.description
    'This folder is just for functional tests.'
    >>> f.rdfDataSource
    'testscheme://localhost/biomarkers/a'
    >>> f.bmoDataSource
    'testscheme://localhost/biomarkerorgans/a'
    >>> f.disclaimer
    'You are legally obligated to not use these biomarkers.'

Biomarker Folders hold biomarkers as well as other Biomarker Folders.  We'll
test adding biomarkers below, but let's make sure there's a link to created
nested Biomarker Folders::

    >>> browser.open(portalURL + '/questionable-biomarkers')
    >>> l = browser.getLink(id='biomarker-folder')
    >>> l.url.endswith('createObject?type_name=Biomarker+Folder')
    True


Elemental Biomarker
~~~~~~~~~~~~~~~~~~~

An Elemental Biomarker object represents a single real-world biomarker being
researched and developed as an early indicator for cancer by EDRN.  They may
be created only with Biomarker Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='elemental-biomarker')
    Traceback (most recent call last):
    ...
    LinkNotFoundError

So, let's create one in our above Biomarker Folder.  Before we start setting up
attributes, though, we'll need some related objects that biomarker have links
to.  A biomarker refers to protocols::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='study-folder').click()
    >>> browser.getControl(name='title').value = 'Questionable Studies'
    >>> browser.getControl(name='description').value = 'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/protocols/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/questionable-studies/ingest')

A biomarker also refers to body systems::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='knowledge-folder').click()
    >>> browser.getControl(name='title').value = u'My Private Parts'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/bodysystems/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/my-private-parts/ingest')

And to publications::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='publication-folder').click()
    >>> browser.getControl(name='title').value = u'Ye Olde Bookshelfe'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/pubs/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/ye-olde-bookshelfe/ingest')

And to miscellaneous resources::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='knowledge-folder').click()
    >>> browser.getControl(name='title').value = u'Ye Olde Intarwebz'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/resources/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/ye-olde-intarwebz/ingest')

And to ECAS datasets::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='dataset-folder').click()
    >>> browser.getControl(name='title').value = u'Ye Olde Data Warehouse'
    >>> browser.getControl(name='description').value = u'This folder is just for functional tests.'
    >>> browser.getControl(name='rdfDataSource').value = u'testscheme://localhost/datasets/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/ye-olde-data-warehouse/ingest')

Now we can create a testing Elemental Biomarker::

    >>> browser.open(portalURL + '/questionable-biomarkers')
    >>> l = browser.getLink(id='elemental-biomarker')
    >>> l.url.endswith('createObject?type_name=Elemental+Biomarker')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = 'Phthalate'
    >>> browser.getControl(name='description').value = "It's fun to say."
    >>> browser.getControl(name='identifier').value = 'http://edrn/biomarkers/24'
    >>> browser.getControl(name='shortName').value = 'Phbtbthpt!'
    >>> browser.getControl(name='hgncName').value = 'X1' # CA-1235
    >>> browser.getControl(name='bmAliases:lines').value = 'anal ahem\nbackfire\nbean blower\nBlow the big brown horn'
    >>> browser.getControl(name='biomarkerType').value = 'Gas'
    >>> browser.getControl(name='qaState').value = 'Under Review'
    >>> browser.getControl(name='protocols:list').displayValue = ["Public Safety"]
    >>> browser.getControl(name='publications:list').displayValue = ["Letter to the editor: SeqXML and OrthoXML: standards for sequence and orthology information."]
    >>> browser.getControl(name='resources:list').displayValue = ['A search engine', 'A web index']
    >>> browser.getControl(name='datasets:list').displayValue = ['Get Bent']
    >>> browser.getControl(name='accessGroups:lines').value = 'ldap://access.this/1'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'phthalate' in f.objectIds()
    True
    >>> biomarker = f['phthalate']
    >>> biomarker.title
    u'Phthalate'
    >>> biomarker.description
    "It's fun to say."
    >>> biomarker.identifier
    'http://edrn/biomarkers/24'
    >>> biomarker.shortName
    'Phbtbthpt!'
    >>> biomarker.hgncName
    'X1'
    >>> biomarker.bmAliases
    ('anal ahem', 'backfire', 'bean blower', 'Blow the big brown horn')
    >>> biomarker.biomarkerType
    'Gas'
    >>> biomarker.qaState
    'Under Review'
    >>> biomarker.protocols[0].title
    'Public Safety'
    >>> biomarker.publications[0].title
    'Letter to the editor: SeqXML and OrthoXML: standards for sequence and orthology information.'
    >>> resources = [i.title for i in biomarker.resources]
    >>> resources.sort()
    >>> resources
    ['A search engine', 'A web index']
    >>> biomarker.datasets[0].title
    'Get Bent'
    >>> biomarker.accessGroups
    ('ldap://access.this/1',)

Heather Kincaid reported (not via the issue tracker, unfortunately) that the
URLs to datasets should go into ECAS.  Do they?  Let's look::

    >>> browser.contents
    '...href="urn:edrn:top-secret-data"...Get Bent...'

Yes.


Biomarker Body System
~~~~~~~~~~~~~~~~~~~~~

An Elemental Biomarker may itself contain additional objects the further
describe the biomarker's affects on body systems; these are called Biomarker
Body Systems.  They may be added only to Elemental Biomarkers, vis::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='biomarker-body-system')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.open(portalURL + '/questionable-biomarkers/phthalate')
    >>> l = browser.getLink(id='biomarker-body-system')
    >>> l.url.endswith('createObject?type_name=Biomarker+Body+System')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = 'Anus'
    >>> browser.getControl(name='description').value = 'Flatus-based biomarkers provide several indicators for the anus.'
    >>> browser.getControl(name='performanceComment').value = 'The biomarker failed to perform as expected.'
    >>> browser.getControl(name='identifier').value = 'http://edrn/biomarkers/24/3'
    >>> browser.getControl(name='bodySystem:list').displayValue = ['Anus']
    >>> browser.getControl(name='protocols:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='publications:list').displayValue = ['Early detection biomarkers for ovarian cancer.']
    >>> browser.getControl(name='resources:list').displayValue = ['A web index']
    >>> browser.getControl(name='cliaCertification:boolean').value = True
    >>> browser.getControl(name='fdaCertification:boolean').value = True
    >>> browser.getControl(name='phase').value = '2'
    >>> browser.getControl(name='qaState').value = 'High'
    >>> browser.getControl(name='form.button.save').click()
    >>> 'anus' in biomarker.objectIds()
    True
    >>> biomarkerOrgan = biomarker['anus']
    >>> biomarkerOrgan.title
    u'Anus'
    >>> biomarkerOrgan.description
    'Flatus-based biomarkers provide several indicators for the anus.'
    >>> biomarkerOrgan.performanceComment
    'The biomarker failed to perform as expected.'
    >>> biomarkerOrgan.identifier
    'http://edrn/biomarkers/24/3'
    >>> biomarkerOrgan.bodySystem.title
    'Anus'
    >>> biomarkerOrgan.protocols[0].title
    'Public Safety'
    >>> biomarkerOrgan.publications[0].title
    'Early detection biomarkers for ovarian cancer.'
    >>> biomarkerOrgan.resources[0].title
    'A web index'
    >>> biomarkerOrgan.cliaCertification
    True
    >>> biomarkerOrgan.fdaCertification
    True
    >>> biomarkerOrgan.phase
    '2'
    >>> biomarkerOrgan.qaState
    'High'


Body System Study
~~~~~~~~~~~~~~~~~
    
Biomarker Body Systems further contain objects that identify what studies and
protocols analyzed the indications of the biomarker with regard to the body
system.  These are represented by Body System Study objects, which can be made
solely within Biomarker Body Systems::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='body-system-study')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.open(portalURL + '/questionable-biomarkers/phthalate')
    >>> browser.getLink(id='body-system-study')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.open(portalURL + '/questionable-biomarkers/phthalate/anus')
    >>> l = browser.getLink(id='body-system-study')
    >>> l.url.endswith('createObject?type_name=Body+System+Study')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = 'Mr Goatse: A Closer Look at the Anus'
    >>> browser.getControl(name='decisionRule').value = 'A sample decision rule'
    >>> browser.getControl(name='identifier').value = 'http://edrn/biomarkers/24/3/6'
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='protocols:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='publications:list').displayValue = ['Letter to the editor: SeqXML and OrthoXML: standards for sequence and orthology information.']
    >>> browser.getControl(name='resources:list').displayValue = ['A web index']
    >>> browser.getControl(name='form.button.save').click()
    >>> bodySystemStudy = biomarkerOrgan['mr-goatse-a-closer-look-at-the-anus']
    >>> bodySystemStudy.title
    u'Mr Goatse: A Closer Look at the Anus'
    >>> bodySystemStudy.decisionRule
    'A sample decision rule'
    >>> bodySystemStudy.identifier
    'http://edrn/biomarkers/24/3/6'
    >>> bodySystemStudy.protocol.title
    'Public Safety'
    >>> bodySystemStudy.protocols[0].title
    'Public Safety'
    >>> bodySystemStudy.publications[0].title
    'Letter to the editor: SeqXML and OrthoXML: standards for sequence and orthology information.'
    >>> bodySystemStudy.resources[0].title
    'A web index'


Study Statistics
~~~~~~~~~~~~~~~~

Biomarker Body Systems as well contain objects: Study Statistics.  These
represent statistical analyses performed within the protocol or study and
relevant to the indication for the biomarker on the body system.  They may be
created within Body System Study objects only::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='study-statistics')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.open(portalURL + '/questionable-biomarkers/phthalate')
    >>> browser.getLink(id='study-statistics')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.open(portalURL + '/questionable-biomarkers/phthalate/anus')
    >>> browser.getLink(id='study-statistics')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.open(portalURL + '/questionable-biomarkers/phthalate/anus/mr-goatse-a-closer-look-at-the-anus')
    >>> l = browser.getLink(id='study-statistics')
    >>> l.url.endswith('createObject?type_name=Study+Statistics')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = 'Statistic 1'
    >>> browser.getControl(name='identifier').value = 'http://edrn/biomarkers/24/3/6/statistic-1'
    >>> browser.getControl(name='sensitivity').value = '0.9'
    >>> browser.getControl(name='specificity').value = '0.3'
    >>> browser.getControl(name='npv').value = '0.6'
    >>> browser.getControl(name='ppv').value = '0.4'
    >>> browser.getControl(name='prevalence').value = '0.5'
    >>> browser.getControl(name='details').value = 'The anus was quite sensitive to the biomarker.'
    >>> browser.getControl(name='specificAssayType').value = 'Sample specific assay type details.'
    >>> browser.getControl(name='form.button.save').click()
    >>> studyStatistic = bodySystemStudy['statistic-1']
    >>> studyStatistic.title
    'Statistic 1'
    >>> studyStatistic.identifier
    'http://edrn/biomarkers/24/3/6/statistic-1'
    >>> studyStatistic.sensitivity >= 0.9
    True
    >>> studyStatistic.specificity <= 0.3
    True
    >>> studyStatistic.npv <= 0.6
    True
    >>> studyStatistic.ppv >= 0.4
    True
    >>> studyStatistic.prevalence
    0.5
    >>> studyStatistic.details
    'The anus was quite sensitive to the biomarker.'
    >>> studyStatistic.specificAssayType
    'Sample specific assay type details.'


Biomarker Panel
~~~~~~~~~~~~~~~

A Biomarker Panel is a composite biomarker.  It has some of the properties of
a single biomarker while delegating other properties to its member markers.
As with Elemental Biomarkers, Biomarker Panels may be created solely within
Biomarker Folders::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='biomarker-panel')
    Traceback (most recent call last):
    ...
    LinkNotFoundError
    >>> browser.open(portalURL + '/questionable-biomarkers')
    >>> l = browser.getLink(id='biomarker-panel')
    >>> l.url.endswith('createObject?type_name=Biomarker+Panel')
    True
    >>> l.click()
    >>> browser.getControl(name='title').value = 'Various Secretions'
    >>> browser.getControl(name='description').value = 'A number of biomarkers collected during a certain activity.'
    >>> browser.getControl(name='identifier').value = 'urn:edrn:various-secretions'
    >>> browser.getControl(name='shortName').value = 'VS'
    >>> browser.getControl(name='qaState').value = 'Hoopy'
    >>> browser.getControl(name='bmAliases:lines').value = 'Various S\nV Secretions'
    >>> browser.getControl(name='members:list').displayValue = ['Phthalate']
    >>> browser.getControl(name='form.button.save').click()
    >>> panel = f['various-secretions']
    >>> panel.title
    u'Various Secretions'
    >>> panel.description
    'A number of biomarkers collected during a certain activity.'
    >>> panel.identifier
    'urn:edrn:various-secretions'
    >>> panel.shortName
    'VS'
    >>> panel.bmAliases
    ('Various S', 'V Secretions')
    >>> panel.qaState
    'Hoopy'
    >>> panel.members[0].title
    u'Phthalate'

Biomarker Panels should behave just like Elemental Biomarkers in that they may
contain nested Biomarker Body Systems (which contain Body System Study
objects, which contain Study Statistics). Adding those objects to our panel::

    >>> browser.getLink(id='biomarker-body-system').click()
    >>> browser.getControl(name='title').value = 'Rectum'
    >>> browser.getControl(name='description').value = 'Flatus-based biomarkers provide several indicators for the rectum.'
    >>> browser.getControl(name='identifier').value = 'urn:edrn:various-secretions:rectum'
    >>> browser.getControl(name='bodySystem:list').displayValue = ['Rectum']
    >>> browser.getControl(name='protocols:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='publications:list').displayValue = ['Early detection biomarkers for ovarian cancer.']
    >>> browser.getControl(name='resources:list').displayValue = ['A search engine']
    >>> browser.getControl(name='phase').value = '5'
    >>> browser.getControl(name='qaState').value = 'Low'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink(id='body-system-study').click()
    >>> browser.getControl(name='title').value = 'Mr Anus: A Closer Look at the Rectum'
    >>> browser.getControl(name='identifier').value = 'urn:edrn:various-secretions:rectum:anus'
    >>> browser.getControl(name='protocol:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='protocols:list').displayValue = ['Public Safety']
    >>> browser.getControl(name='publications:list').displayValue = ['Letter to the editor: SeqXML and OrthoXML: standards for sequence and orthology information.']
    >>> browser.getControl(name='resources:list').displayValue = ['A web index']
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink(id='study-statistics').click()
    >>> browser.getControl(name='title').value = 'Anal 1'
    >>> browser.getControl(name='identifier').value = 'urn:edrn:various-secretions:rectum:anus:anal-1'
    >>> browser.getControl(name='sensitivity').value = '0.1'
    >>> browser.getControl(name='specificity').value = '0.2'
    >>> browser.getControl(name='npv').value = '0.3'
    >>> browser.getControl(name='ppv').value = '0.4'
    >>> browser.getControl(name='prevalence').value = '0.5'
    >>> browser.getControl(name='details').value = 'The rectum was quite sensitive.'
    >>> browser.getControl(name='form.button.save').click()

Why demonstrate adding all that?  Well, to ensure it works for one, but also
to make sure views of the panel work when we test the templates.


Templates
---------

In this section, we'll do some quick functional-esque tests of the page
templates providing views of a couple objects.


HGNC Names
~~~~~~~~~~

CA-1235 introduces HGNC_ names to biomarkers::

    >>> browser.open(portalURL + '/questionable-biomarkers/phthalate')
    >>> browser.contents
    '...HGNC Name:...X1...'

Works!  Related to this is CA-1247, which wants links from biomarkers to
BioMuta_.  Are those links there?  Check it out::

    >>> browser.contents
    '...a href="https://hive.biochemistry.gwu.edu/tools/biomuta/biomuta.php?gene=X1"...'    

Wootly.


Members of Panels
~~~~~~~~~~~~~~~~~

Issue http://oodt.jpl.nasa.gov/jira/browse/CA-430 claims the members of
biomarker panels don't appear.  Well, we'll soon see about that!  Here's our
panel from earlier::

    >>> browser.open(portalURL + '/questionable-biomarkers/various-secretions')
    >>> browser.contents
    '...Various Secretions...Panel Details...Phthalate...'

See?  No problem.


Body Systems vs Organs
~~~~~~~~~~~~~~~~~~~~~~

Issue http://oodt.jpl.nasa.gov/jira/browse/CA-411 stipulated that the newer
term, "body systems", was in fact not correct and we needed to use the older
term, "organs".  Oy vey.

OK, viewing our elemental biomarker again::

    >>> browser.open(portalURL + '/questionable-biomarkers/phthalate')
    >>> 'Body Systems' in browser.contents
    False
    >>> browser.contents
    '...<h2 class="approved">...Organs...</h2>...'

And the panel::

    >>> browser.open(portalURL + '/questionable-biomarkers/various-secretions')
    >>> 'Body Systems' in browser.contents
    False
    >>> browser.contents
    '...<h2 class="approved">...Organs...</h2>...'


Biomarker Folder View
~~~~~~~~~~~~~~~~~~~~~

Previously, we used a simple alphabetical view.  No more.  Now we have a nifty
faceted view::

    >>> browser.open(portalURL + '/questionable-biomarkers')
    >>> browser.contents
    '...faceted-results...'

Also, there are other views providing what Dan calls "biomarker analytics"::

    >>> browser.contents
    '...PIs by Biomarker...'

Neat, huh?


RDF Ingestion
-------------

Biomarker folders have a method that can be invoked via traversal that causes
them to ingest content from a pre-defined RDF data source.  That source is the
EDRN Biomarker Database (BMDB_).  The BMDB enables curators to enter, update,
search for, and retrieve biomarkers.

Of course, the portal can do all that too, but for some reason our boss wanted
a separate application, causing another developer to essentially duplicate all
the work that goes into the portal (and with dubious PHP-based products no
less), ignoring all of the automatically-generated forms, validation, and
security that the portal provides for free.

Clearly, this is a *government project*.

So, let's create a new biomarker folder and have it ingest some RDF::

    >>> browser.open(portalURL)
    >>> browser.getLink(id='biomarker-folder').click()
    >>> browser.getControl(name='title').value = 'Tacky Biomarkers'
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/biomarkers/a'
    >>> browser.getControl(name='bmoDataSource').value = 'testscheme://localhost/biomarkerorgans/a'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.open(portalURL + '/tacky-biomarkers/content_status_modify?workflow_action=publish')
    >>> f = portal['tacky-biomarkers']

Note that Biomarker Folders require two RDF data sources unlike the
``eke.knowledge`` folder and its subclasses.  For some reason, the BMDB
exports its knowledge this way.

Ingesting::

    >>> browser.open(portalURL + '/tacky-biomarkers/ingest')
    >>> browser.contents
    '...The following items have been created...Apogee 1...'
    >>> 'APG1' in f.objectIds()
    True
    >>> 'panel-1' in f.objectIds()
    True
    >>> a1 = f['APG1']
    >>> a1.title
    u'Apogee 1'
    >>> a1.hgncName
    'APG1'
    >>> a1.description
    'A sticky bio-marker.'
    >>> a1.shortName
    'A1'
    >>> 'Approach' in a1.bmAliases, 'Advent' in a1.bmAliases, 'Bigo' in a1.bmAliases
    (True, True, True)
    >>> a1.biomarkerType
    'Colloidal'
    >>> a1.identifier
    'http://edrn/bmdb/a1'
    >>> a1.publications[0].title
    'Early detection biomarkers for ovarian cancer.'
    >>> a1.resources[0].title
    'A web index'

Noticed that the Apogee 1 got its HGNC_ name (APG1) as its object ID. The panel
doesn't have an HGNC name, so it took its object ID from the title (CA-1235).

I'm seeing non-deterministic behavior from the Plone Catalog, which results in
no protocols appearing, but just *sometimes*.  Ugh.  So::

    >>> 0 <= len(a1.protocols) <= 2
    True

Thanks a lot, ZCatalog.  Continuing::

    >>> a1.datasets[0].title
    'Get Bent'
    >>> a1.qaState
    'Accepted'
    >>> o1 = a1['rectum']
    >>> o1.title
    u'Rectum'
    >>> o1.description
    'Action on the rectum is amazing.'
    >>> o1.performanceComment
    'The biomarker failed to perform as expected.'
    >>> o1.bodySystem.title
    'Rectum'
    >>> o1.cliaCertification
    True
    >>> o1.fdaCertification
    False
    >>> o1.phase
    '1'
    >>> o1.qaState
    'Accepted'
    >>> o1.identifier
    'http://edrn/bmdb/a1/o1'
    >>> o1.publications[0].title
    'Letter to the editor: SeqXML and OrthoXML: standards for sequence and orthology information.'
    >>> s1 = o1['public-safety']
    >>> s1.protocol.title
    'Public Safety'
    >>> s1.decisionRule
    'A sample decision rule'
    >>> s1.phase
    '1'
    >>> for i in s1.objectIds():
    ...     stats = s1[i]
    ...     stats.sensitivity in (1.0, 6.0)
    ...     True
    ...     stats.specificity in (2.0, 7.0)
    ...     True
    ...     stats.npv in (4.0, 9.0)
    ...     True
    ...     stats.ppv in (5.0, 10.0)
    ...     True
    ...     stats.prevalence in (3.0, 8.0)
    ...     True
    ...     stats.details in ('The first one', 'The second two')
    ...     True
    ...     stats.specificAssayType == 'Sample specific assay type details'
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    True
    >>> panel = f['panel-1']
    >>> panel.title
    u'Panel 1'
    >>> panel.shortName
    'P1'
    >>> panel.identifier
    'http://edrn/bmdb/p1'
    >>> panel.description
    'A very sticky panel.'
    >>> panel.members[0].title
    u'Apogee 1'

Re-ingesting shouldn't duplicate any biomarkers::

    >>> len(f.objectIds())
    2
    >>> browser.open(portalURL + '/tacky-biomarkers/ingest')
    >>> len(f.objectIds())
    2

Ingesting biomarkers should also update their indicated organs which are
displayed on the folder::

    >>> browser.open(portalURL + '/tacky-biomarkers/@@view')
    >>> browser.contents
    '...Apogee 1...Rectum...Panel 1...'


Protocol Associations
~~~~~~~~~~~~~~~~~~~~~

http://oodt.jpl.nasa.gov/jira/browse/CA-425 noted that protocols should link
to biomarkers (as well as to datasets).  Protocol information in the protocol
RDF doesn't explicitly give such associations, however the RDF from biomarkers
does.

Does such ingest link a protocol to a biomarker?  Let's find out::

    >>> browser.open(portalURL + '/questionable-studies/ps-public-safety')
    >>> browser.contents
    '...Public Safety...Biomarkers...Apogee 1...'

Meanwhile, CA-620 complains that lock icons are showing up on Biomarkers, when
we've changed the behavior of Biomarkers (thanks to CA-650) so that lock icons
don't appear at all anymore.  The upshot of all this is that everyone can view
the basic details of biomarkers, so the lock icons appearing on a protocol
page, even for incorrectly secured biomarkers, is now moot.  There should be
no lock icons at all.  Are there?  First, let's make one of the biomarkers
private::

    >>> browser.open(portalURL + '/tacky-biomarkers/APG1')
    >>> browser.contents
    '...State:...Published...'

Sadly, under plone.app.testing, we get a non-snazzy workflow, so although I'd
like it to be private, it's not::

    >>> browser.open(portalURL + '/tacky-biomarkers/APG1/content_status_modify?workflow_action=retract')
    >>> browser.contents
    '...State:...Public draft...'

Close enough for government work.

Now let's check the protocol, which previously was using publication state to
toss a lock icon onto things::

    >>> browser.open(portalURL + '/questionable-studies/ps-public-safety')
    >>> 'Unreleased biomarker' in browser.contents
    False
    >>> 'lock_icon' in browser.contents
    False

Looks like we're all clear.  Let's put Apogee 1 back to where it belongs
(non-snazzy workflow notwithstanding)::

    >>> browser.open(portalURL + '/tacky-biomarkers/APG1')
    >>> browser.contents
    '...State:...Public draft...'
    >>> browser.open(portalURL + '/tacky-biomarkers/APG1/content_status_modify?workflow_action=publish')
    >>> browser.contents
    '...State:...Published...'


Security
~~~~~~~~

Biomarkers contain sensitive information that we can't have the general public
go and read about until they've been officially released.  The RDF contains
information that tells if a biomarker is public or private, and if it's
private, what groups are allowed to access it.

To demonstrate this functionality, let's revisit Apogee 1 and note its
publication state::

    >>> browser.open(portalURL + '/tacky-biomarkers/APG1')
    >>> browser.contents
    '...State:...Published...'

Furthermore, the nested objects should likewise be published (or else CA-342
isn't fixed)::

    >>> apogee1 = f['APG1']
    >>> wfTool = getToolByName(portal, 'portal_workflow')
    >>> rectum = apogee1['rectum']
    >>> wfTool.getInfoFor(rectum, 'review_state')
    'published'
    >>> publicSafety = rectum['public-safety']
    >>> wfTool.getInfoFor(publicSafety, 'review_state')
    'published'
    >>> for i in publicSafety.objectIds():
    ...     stat = publicSafety[i]
    ...     wfTool.getInfoFor(stat, 'review_state')
    'published'
    'published'
    
Great.  CA-650 says though that private biomarkers should still be published,
but *some* of their details shouldn't be visible.  Let's reload from an RDF
source that defines a biomarker that's currently under review::

    >>> browser.open(portalURL + '/tacky-biomarkers/edit')
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/biomarkers/b'
    >>> browser.getControl(name='bmoDataSource').value = 'testscheme://localhost/biomarkerorgans/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()

OK, is it published?

    >>> browser.open(portalURL + '/tacky-biomarkers/BB')
    >>> browser.contents
    '...State:...Published...'

So far so good.  This marker's accessor list should contain the URI of the
group that is allowed to see it::

    >>> b1 = f['BB']
    >>> b1.accessGroups
    ('ldap://edrn/groups/g1',)

The Sharing tab on the marker should also show that the "g1" group is allowed
full access to the biomarker::

    >>> browser.open(portalURL + '/tacky-biomarkers/BB/@@sharing')
    >>> browser.contents
    '...Name...ldap://edrn/groups/g1...'

We're currently logged in with rather superior privileges, so we should be
able to view information beyond the basics::

    >>> browser.open(portalURL + '/tacky-biomarkers/BB')
    >>> browser.contents
    '...Basics...Ooze...Organs...Anus...Publications...Early detection...'
    >>> 'This biomarker is currently being annotated or is under review' not in browser.contents
    True

Note also that the notice about the lock icon is gone from the folder view
too::

    >>> browser.open(portalURL + '/tacky-biomarkers')
    >>> 'This icon indicates content for which you must be logged in or do not have permission to view' not in browser.contents
    True

And a quick check of certifications (we saw CLIA above with /biomarkerorgans/a,
so let's see if we get FDA with /biomarkerorgans/b)::

    >>> b1['anus'].cliaCertification
    False
    >>> b1['anus'].fdaCertification
    True

Woot!  We're ready for the next section!


Empty <hasBiomarkerStudyDatas/> Element
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The BMDB apparently sometimes produces in its RDF export a biomarker-organ
description that includes an empty <hasBiomarkerStudyDatas/>.  Let's make sure
that empty element doesn't cause ingest problems.  The data source at
``testscheme://localhost/biomarkerorgans/b`` happens to include just such an
empty element.  Ingesting::

    >>> browser.open(portalURL + '/tacky-biomarkers/edit')
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/biomarkers/b'
    >>> browser.getControl(name='bmoDataSource').value = 'testscheme://localhost/biomarkerorgans/b'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> browser.contents
    '...The following items have been created...Bile 1...'

See? No error! That's it.


RDF Data Sources
~~~~~~~~~~~~~~~~

The URL to an RDF data source is nominally displayed on a knowledge folder::

    >>> browser.open(portalURL + '/tacky-biomarkers/@@view')
    >>> browser.contents
    '...RDF Data Source...testscheme://localhost/biomarkers/b...Biomarker-Organs Data Source...testscheme://localhost/biomarkerorgans/b...'

That shows up because we're logged in as an administrator.  Mere mortals
shouldn't see that::

    >>> unprivilegedBrowser.open(portalURL + '/tacky-biomarkers/@@view')
    >>> 'RDF Data Source' not in unprivilegedBrowser.contents
    True
    >>> 'Biomarker-Organs Data Source' not in unprivilegedBrowser.contents
    True


Searching
---------

Searching biomarkers naturally uses its title and descriptive text, but we
also want to search by body systems.  Let's see if that works.

    >>> catalog = getToolByName(portal, 'portal_catalog')
    >>> results = catalog.unrestrictedSearchResults(SearchableText='Anus Biomarker')
    >>> [i.Title for i in results if i.portal_type == 'Elemental Biomarker']
    ['Bile 1', 'Phthalate']

Works for me.  However, issue http://oodt.jpl.nasa.gov/jira/browse/CA-511 says
we need to search on alternative biomarker names as well.  Does that work?
Let's find out::

    >>> results = catalog.unrestrictedSearchResults(SearchableText='Ooze')
    >>> [i.Title for i in results if i.portal_type == 'Elemental Biomarker']
    ['Bile 1']

Fantastic.


Bad Protocols
-------------

CA-1163 tells that if a protocol can't be found for a biomarker, it raises an
exception and aborts the whole ingest.  Instead, it should just leave the
protocol blank and continue onto the next marker.  Let's see if we have such
an error::

    >>> browser.open(portalURL + '/tacky-biomarkers/edit')
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/biomarkers/bad-study'
    >>> browser.getControl(name='bmoDataSource').value = 'testscheme://localhost/biomarkerorgans/bad-study'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()
    >>> browser.contents
    '...The following items have been created...Bad Study...'

No error!


Private Biomarkers
------------------

CA-1182 wants us to have private biomarkers.  These are biomarkers (and their
child objects) that get a private workflow state, so that only users in the
Sharing tab for the marker who have "read" permission can read it.  In the RDF
they have a "QAState" of "Private".

From the section above, we have a biomarker that should be public::

    >>> browser.open(portalURL + '/tacky-biomarkers/bad-study')
    >>> browser.contents
    '...State:...Published...'

And even an unprivileged user can view it:

    >>> unprivilegedBrowser.open(portalURL + '/tacky-biomarkers/bad-study')
    >>> unprivilegedBrowser.contents
    '...Bad Study...BS...'

Now let's ingest a private one::

    >>> browser.open(portalURL + '/tacky-biomarkers/edit')
    >>> browser.getControl(name='rdfDataSource').value = 'testscheme://localhost/biomarkers/private'
    >>> browser.getControl(name='bmoDataSource').value = 'testscheme://localhost/biomarkerorgans/private'
    >>> browser.getControl(name='form.button.save').click()
    >>> browser.getLink('Ingest').click()

Our super user can view it, but note the publication state::

    >>> browser.open(portalURL + '/tacky-biomarkers/secret-1')
    >>> browser.contents
    '...State:...state-private...'
    
And our unprivileged user gets redirected to a log in page::

    >>> unprivilegedBrowser.open(portalURL + '/tacky-biomarkers/secret-1')
    >>> unprivilegedBrowser.contents
    '...Login Name...Password...'

Yay!


Openness
--------

CA-1156 wants us to show more attributes of biomarkers, even those that
haven't yet been "accepted".  To support this, there's another new "QAState"
called "Curated" which comes after "Under Review" but before "Accepted".
Let's revisit our "Phthalate" biomarker and change its QA state::

    >>> unprivilegedBrowser.open(portalURL + '/questionable-biomarkers/phthalate')
    >>> unprivilegedBrowser.contents
    '...QA State...Under Review...Organs...under review...Studies...under review...Publications...under review...Resources...under review...'

As you can see, a biomarker under view doesn't reveal very much at all.  Now,
let's change the QA state of Phthalate to "Curated"::

    >>> browser.open(portalURL + '/questionable-biomarkers/phthalate/edit')
    >>> browser.getControl(name='qaState').value = 'Curated'
    >>> browser.getControl(name='form.button.save').click()

Revisiting, we see that some additional organ information is available
(description and performance comment), but none of the supporting data or
statistical information is present::

    >>> unprivilegedBrowser.open(portalURL + '/questionable-biomarkers/phthalate')
    >>> unprivilegedBrowser.contents
    '...QA State...Curated...'
    >>> unprivilegedBrowser.contents
    '...The following organs...Anus...Flatus-based biomarkers...The biomarker failed to perform as expected...'
    >>> 'Supporting Study Data' in unprivilegedBrowser.contents
    False
    >>> 'Mr Goatse: A Closer Look at the Anus' in unprivilegedBrowser.contents
    False
    >>> 'Biomarker Characteristics Summary' in unprivilegedBrowser.contents
    False
    >>> 'Sensitivity' in unprivilegedBrowser.contents
    False
    >>> 'Decision Rule' in unprivilegedBrowser.contents
    False
    >>> 'Additional Study-Specific Protocols' in unprivilegedBrowser.contents
    False
    >>> 'Study-Specific Publications' in unprivilegedBrowser.contents
    False
    >>> 'Study-Specific Resources' in unprivilegedBrowser.contents
    False
    >>> 'Organ-Specific Protocols' in unprivilegedBrowser.contents
    False
    >>> 'Organ-Specific Publications' in unprivilegedBrowser.contents
    False
    >>> 'Organ-Specific Resources' in unprivilegedBrowser.contents
    False

No information from the Studies tab should show up::

    >>> unprivilegedBrowser.contents
    '...QA State...Curated...Organs...Studies...under review...'

But publications are fine::

    >>> unprivilegedBrowser.contents
    '...QA State...Curated...Organs...Studies...Publications...Letter to the editor...'

And resources are OK too::

    >>> unprivilegedBrowser.contents
    '...QA State...Curated...Organs...Studies...Publications...Resources...A search engine...A web index...'

And that's it.


.. References:
.. _EKE: http://cancer.jpl.nasa.gov/documents/applications/knowledge-environment
.. _RDF: http://w3.org/RDF/
.. _URI: http://w3.org/Addressing/
.. _BMDB: http://edrn.jpl.nasa.gov/bmdb
.. _HGNC: http://www.genenames.org/
.. _BioMuta: http://hive.biochemistry.gwu.edu/tools/biomuta/index.php

