========
EEA Epub
========
A product which allows you to import in Plone epub files.


Contents
========

.. contents::


Introduction
============

EEA Epub product allows you to import in Plone epub files. On upload,
Epub content will imported as Plone folders, files, images and documents.

Export to Epub is also available.

As of version 4.3 epub files created with **Adobe InDesign CS4** and **Sigil**
are tested and known to work with this package, previous versions of this
package only supported epubs created with InDesign.


Main features
=============

EEA Epub features:

1. Imports epub files as Plone content.
2. Stores the original epub in the main folder for easy retrieval.
3. Exports the Plone content back into an epub.
4. Clean filename as you import the epub and they contain characters that
   wouldn't be allowed as a Plone id.
   This behaviour is on by default but it can be disabled by unchecking
   the boolean flag at portal_properties/site_properties
   **clean_epub_file_names**.
   If you find that the Document Pages added by the Epub process has broken
   links try to re-upload without this boolean flag.
5. Possibility to temporarily disable dynamic ePub creation by adding an item
   called 'action-download-epub' within context
6. Asynchronously generate ePub files and notify users by email
   when ePub is ready


Epub compatibility
==================

EEA Epub makes the following assumptions about the loaded epub:

1. You don't use unicode or other special characters into the name
   of the epub, images or links
2. You've created the epub with "Adobe InDesign CS4" or "Sigil" which uses
   some standards for the following:

   * The table of contents is named toc.ncx and is placed inside OEBPS
   * Book text & images are placed inside the folder OEBPS or other folders
     that are children of OEBPS
   * Items ids doesn't contain the following characters . / \ ( if
     possible stick to letters, numbers and - _ )

Best practices when creating an epub:

1. Chapter names should not be all uppercase or use special characters
2. Image names should not contain spaces, periods, / or other special characters


Debugging
=========

At this moment any errors that would appear on the site are surpressed
with a info message.

If you want to see the detailed error check the Plone instance log usually
found in buildout-folder/var/log.


Installation
============

The easiest way to get eea.epub support in Plone 4 using this
package is to work with installations based on `zc.buildout`_.
Other types of installations should also be possible, but might turn out
to be somewhat tricky.

To get started you will simply need to add the package to your **eggs** and
**zcml** sections, run buildout, restart your Plone instance and install the
**eea.epub** package using the quick-installer or via the "Add-on
Products" section in "Site Setup"::

    [instance]
    eggs =
        eea.epub

    zcml =
        eea.epub

You can download a sample buildout at:

https://github.com/eea/eea.epub/tree/master/buildouts/plone4

Asynchronous setup
------------------
By default all ePubs are **NOT** generated asynchronous. You'll need `eea.pdf`_
installed in order to be able to enable asynchronous download or you can
provide an os environment called **EEACONVERTER_ASYNC**.

Also some extra config is needed within your buildout in order for this
to work properly.

First of all you'll need a folder were to store generated ePub files. For this
you can create it manually within buildout:directory/var/ or
you can let buildout handle it::

    [buildout]

    parts +=
        media-downloads
        media-downloads-temp

    media-downloads-path = ${buildout:directory}/var/downloads/pdf
    media-downloads-temp = ${buildout:directory}/var/downloads/tmp

    [media-downloads]
    recipe = ore.recipe.fs:mkdir
    path = ${buildout:media-downloads-path}
    mode = 0700
    createpath = true

    [media-downloads-temp]
    recipe = ore.recipe.fs:mkdir
    path = ${buildout:media-downloads-temp}
    mode = 0700
    createpath = true

This will create a folder named **downloads** within buildout:directory/var/

Next, in order for this folder to be visible from your website and your users to
be able to download generated ePubs you'll need to tell to your zope instances
about it::

    [buildout]

    media-downloads-name = downloads
    media-downloads-path = ${buildout:directory}/var/downloads/pdf
    media-downloads-temp = ${buildout:directory}/var/downloads/tmp

    [instance]

    environment-vars +=
      EEADOWNLOADS_NAME ${buildout:media-downloads-name}
      EEADOWNLOADS_PATH ${buildout:media-downloads-path}
      EEACONVERTER_TEMP ${buildout:media-downloads-temp}
      EEACONVERTER_ASYNC True

Also, don't forget to setup `plone.app.async`_

::

    [buildout]

    [instance]
    eggs +=
        plone.app.async
    zcml +=
        plone.app.async-single_db_worker


Getting started
===============

Import
------
From "Add new" menu select "EpubFile" and upload an epub file.

Export
------
Go to Home page and click on download as ePub icon at the bottom of the page
 or directly access http://localhost:8080/Plone/front-page/download.epub


Custom permissions
==================
Custom permissions added by this package

Can download ePub (eea.epub.download)
-------------------------------------
Assign this permission to roles that you want to be able to download content as ePub
Default: Owner, Manager, Editor

Can customize ePub (eea.epub.customize)
---------------------------------------
Assign this permission to roles that you want to be able to contextually customize
the output ePub look and feel
Default: Manager, Site Administrator

Content rules
=============
This package uses Plone Content-rules to notify users by email when an asynchronous
ePub job is done. Thus 3 custom content-rules will be added within
Plone > Site Setup > Content-rules

.. warning ::

  As these content-rules are triggered by an asynchronous job, while
  you customize the email template for these content-rules,
  please **DO NOT USE OTHER** string substitutions **that the ones** that start
  with **$download_** as you'll break the download chain.
  Also if you disable these content-rules the users will never know when the
  ePub is ready and what is the link where they can download the output ePub.

ePub export succeeded
---------------------
Notify the person who requested a ePub export that the ePub successfully exported
and provide a link to the downloadable ePub

ePub export failed
------------------
Notify the person who requested a ePub export that the ePub export failed.

ePub export failed (admin)
--------------------------
Notify admin that there were issues while exporting ePub


Content rules email string substitution
=======================================
In order to be able to easily customize emails sent by this package the following
custom email template string substitutions can be made


${download_came_from_url}
-------------------------
The absolute URL of the Plone object which is downloaded as ePub

${download_email}
-----------------
Email address of the user that triggered the download as ePub action

${download_error}
-----------------
Error traceback when download as ePub job fails

${download_from_email}
----------------------
Site Admin email address customizable via Plone > Site Setup > Mail

${download_from_name}
---------------------
Site Admin name customizable via Plone > Site Setup > Mail

${download_title}
-----------------
Title of the Plone object which is downloaded as ePub

${download_url}
---------------
The absolute URL where the generated output ePub can be downloaded

${download_type}
----------------
Download type. Default to EPUB for this package. It is package specific and it
can be EPUB, PDF, etc.


Disable ePub export
===================
You have the possibility to temporarily disable dynamic ePub export contextually
by adding a static ePub file (or a Python Script, Page Template, etc)
within context called **action-download-epub**. This way /download.epub will
return this file instead of generating one based on context data.

.. note::

  This works only with folderish items.

Content rules
=============
This package uses Plone Content-rules to notify users by email when
an asynchronous ePub job is done. Thus 3 custom content-rules will be added
within Plone > Site Setup > Content-rules

.. warning ::

  As these content-rules are triggered by an asynchronous job, while
  you customize the email template for these content-rules,
  please **DO NOT USE OTHER** string substitutions **that the ones** that start
  with **$download_** as you'll break the download chain.
  Also if you disable these content-rules the users will never know when the
  ePub is ready and what is the link where they can download the output ePub.

Dependecies
===========

1. BeautifulSoup
2. Lxml
3. Plone 4.x
4. `plone.app.async`_
5. `eea.converter`_
6. `eea.downloads`_
7. `eea.pdf`_ (optional for advanced themes and asynchronous download)

Live demo
=========

Here some live production demos at EEA (European Environment Agency)

1. http://www.eea.europa.eu/soer/synthesis


Source code
===========

Latest source code (Plone 4 compatible):
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.epub/trunk

Plone 2 and 3 compatible:
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.epub/branches/plone25


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Epub (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Links
=====

1. EEA Epub wiki page: http://taskman.eionet.europa.eu/projects/zope/wiki/HowToEpub


Funding
=======

EEA_ - European Enviroment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
.. _eea.converter: http://eea.github.com/docs/eea.converter
.. _eea.downloads: http://eea.github.com/docs/eea.downloads
.. _eea.pdf: http://eea.github.com/docs/eea.pdf
.. _plone.app.async: https://github.com/plone/plone.app.async#ploneappasync
.. _zc.buildout: https://pypi.python.org/pypi/zc.buildout
