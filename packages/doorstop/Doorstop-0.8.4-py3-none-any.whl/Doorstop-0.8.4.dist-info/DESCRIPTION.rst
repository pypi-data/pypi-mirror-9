Doorstop
========

| |Build Status|
| |Coverage Status|
| |Scrutinizer Code Quality|
| |PyPI Version|
| |PyPI Downloads|
| |Gittip|

Doorstop manages the storage of textual requirements alongside source
code in version control.

When a project utilizes this tool, each linkable item (requirement, test
case, etc.) is stored as a YAML file in a designated directory. The
items in each directory form a document. The relationship between
documents forms a tree hierarchy. Doorstop provides mechanisms for
modifying this tree, validating item traceability, and publishing
documents in several formats.

Additional reading:

-  publication: `JSEA
   Paper <http://www.scirp.org/journal/PaperInformation.aspx?PaperID=44268#.UzYtfWRdXEZ>`__
-  talks:
   `GRDevDay <https://speakerdeck.com/jacebrowning/doorstop-requirements-management-using-python-and-version-control>`__,
   `BarCamp <https://speakerdeck.com/jacebrowning/strip-searched-a-rough-introduction-to-requirements-management>`__
-  sample: `Generated HTML <http://doorstop.info/reqs/index.html>`__
-  documentation: `API <http://doorstop.info/docs/index.html>`__,
   `Demo <http://nbviewer.ipython.org/gist/jacebrowning/9754157>`__

Getting Started
===============

Requirements
------------

-  Python 3.3+
-  A version control system for requirements storage

Installation
------------

Doorstop can be installed with pip:

::

    $ pip install doorstop

Or directly from source:

::

    $ git clone https://github.com/jacebrowning/doorstop.git
    $ cd doorstop
    $ python setup.py install

After installation, Doorstop is available on the command-line:

::

    $ doorstop --help

And the package is available under the name 'doorstop':

::

    $ python
    >>> import doorstop
    >>> doorstop.__version__

Basic Usage
===========

Document Creation
-----------------

**Parent Document**

After configuring version control, a new parent document can be created:

::

    $ doorstop new REQ ./reqs
    created document: REQ (@/reqs)

Items can be added to the document and edited:

::

    $ doorstop add REQ
    added item: REQ001 (@/reqs/REQ001.yml)

    $ doorstop edit REQ1
    opened item: REQ001 (@/reqs/REQ001.yml)

**Child Documents**

Additional documents can be created that link to other documents:

::

    $ doorstop create TST ./reqs/tests --parent REQ
    created document: TST (@/reqs/tests)

Items can be added and linked to parent items:

::

    $ doorstop add TST
    added item: TST001 (@/reqs/tests/TST001.yml)

    $ doorstop link TST1 REQ1
    linked item: TST001 (@/reqs/tests/TST001.yml) -> REQ001 (@/reqs/REQ001.yml)

Document Validation
-------------------

To check a document hierarchy for consistency, run the main command:

::

    $ doorstop
    valid tree: REQ <- [ TST ]

Document Publishing
-------------------

A text report of a document can be displayed:

::

    $ doorstop publish TST
    1       TST001

            Verify the foobar will foo and bar.

            Links: REQ001

Other formats are also supported:

::

    $ doorstop publish TST --html
    <!DOCTYPE html>
    ...
    <body>
    <h1>1 (TST001)</h1>
    <p>Verify the foobar will foo and bar.</p>
    <p><em>Links: REQ001</em></p>
    </body>
    </html>

Or a file can be created using one of the supported extensions:

::

    $ doorstop publish TST path/to/tst.md
    publishing TST to path/to/tst.md...

Supported formats:

-  Text: **.txt**
-  Markdown: **.md**
-  HTML: **.html**

Content Interchange
-------------------

**Export**

Documents can be exported for editing or to exchange with other systems:

::

    $ doorstop export TST
    TST001:
      active: true
      dervied: false
      level: 1
      links:
      - REQ001
      normative: true
      ref: ''
      text: |
        Verify the foobar will foo and bar.

Or a file can be created using one of the supported extensions:

::

    $ doorstop export TST path/to/tst.csv
    exporting TST to path/to/tst.csv...
    exported: path/to/tst.csv

Supported formats:

-  YAML: **.yml**
-  Comma-Separated Values: **.csv**
-  Tab-Separated Values: **.tsv**
-  Microsoft Office Excel: **.xlsx**

**Import**

Items can be created/updated from the export formats:

::

    $ doorstop import path/to/tst.csv TST

For Contributors
================

Requirements
------------

-  GNU Make:

   -  Windows: http://cygwin.com/install.html
   -  Mac: https://developer.apple.com/xcode
   -  Linux: http://www.gnu.org/software/make (likely already installed)

-  virtualenv: https://pypi.python.org/pypi/virtualenv#installation
-  Pandoc: http://johnmacfarlane.net/pandoc/installing.html
-  Graphviz: http://www.graphviz.org/Download.php

Installation
------------

Create a virtualenv:

::

    make env

Run the tests:

::

    make test
    make tests  # includes integration tests

Build the documentation:

::

    make doc

Run static analysis:

::

    make pep8
    make pep257
    make pylint
    make check  # includes all checks

Prepare a release:

::

    make dist  # dry run
    make upload

.. |Build Status| image:: http://img.shields.io/travis/jacebrowning/doorstop/master.svg
   :target: https://travis-ci.org/jacebrowning/doorstop
.. |Coverage Status| image:: http://img.shields.io/coveralls/jacebrowning/doorstop/master.svg
   :target: https://coveralls.io/r/jacebrowning/doorstop
.. |Scrutinizer Code Quality| image:: http://img.shields.io/scrutinizer/g/jacebrowning/doorstop.svg
   :target: https://scrutinizer-ci.com/g/jacebrowning/doorstop/?branch=master
.. |PyPI Version| image:: http://img.shields.io/pypi/v/Doorstop.svg
   :target: https://pypi.python.org/pypi/Doorstop
.. |PyPI Downloads| image:: http://img.shields.io/pypi/dm/Doorstop.svg
   :target: https://pypi.python.org/pypi/Doorstop
.. |Gittip| image:: http://img.shields.io/badge/gittip-me-brightgreen.svg
   :target: https://www.gittip.com/jacebrowning

Changelog
=========

0.8.4 (2015/03/12)
------------------

- Restrict `openpyxl < 2.2` (there appears to be a breaking change).

0.8.3 (2014/10/10)
------------------

- Fixed a bug running VCS commands in subdirectories.
- Excluded `openpyxl == 2.1.0` as a dependency version.

0.8.2 (2014/09/29)
------------------

- Limit the maximum version of `openpyxl` to 2.1.0 due to deprecation bug.

0.8.1 (2014/09/04)
------------------

- Fixed a bug requesting new item numbers from the server.

0.8 (2014/08/28)
----------------

- Added `doorstop clear ...` to absolve items of their suspect link status.
- Added `doorstop review ...` to absolve items of their unreviewed status.
- Added `Item.clear()` to save stamps (hashes) of linked items.
- Added `Item.review()` to save stamps (hashes) of reviewed items.
- Added `doorstop reorder ...` to organize a document's structure.
- Renamed `Item.id` and `identifer` arguments to `uid`
- Added '--no-body-levels' to `doorstop publish` to hide levels on non-headings.
- Added `doorstop-server` to launch a REST API for UID reservation.
- Added '--server' argument to `doorstop add` to specify the server address.
- Added '--warn-all' and '--error-all' options promote warnings to errors.

0.7.1 (2014/08/18)
------------------

- Fixed bug importing items with empty attributes.

0.7 (2014/07/08)
----------------

- Added `doorstop delete ...` to delete document directories.
- Added `doorstop export ...` to export content for external tools.
- Fixed `doorstop publish ...` handling of unknown formats.
- Added tree structure and traceability to `index.html`.
- Added clickable links using Item IDs in HTML header tags.
- Fixed bug publishing a document to a directory.
- Fixed bug publishing a document without an extension or type specified.
- Updated `doorstop import ...` to import from document export formats.
- Updated `doorstop edit ...` to support document export/import.
- Renamed `doorstop new ...` to `doorstop create ...`.
- Made 'all' a reserved word, which cannot be used as a prefix.

0.6 (2014/05/15)
----------------

- Refactored `Item` levels into a `Level` class.
- Refactored `Item` identifiers into an `ID` class.
- Refactored `Item` text into a `Text` class (behaves like `str`).
- Methods no longer require nor accept 'document' and 'tree' arguments.
- Renamed `Item.find_rlinks()` to `Item.find_child_links()`.
- Changed '--no-rlink-check' to '--no-child-check'.
- Added `Item.find_child_items()` and `Item.find_child_documents()`.
- Added aliases to Item: parent_links, child_links/items/documents.
- Added '--with-child-links' to `doorstop publish` to publish child links.
- Added `doorstop import ...` CLI to import documents and items.
- Refactored `Document` prefixes in a `Prefix` class.
- Added '--no-level-check' to disable document level validation.
- Added '--reorder' option to `doorstop` to enable reordering.

0.5 (2014/04/25)
----------------

- Converted `Item.issues()` to a property and added `Item.get_issues()`.
- Added '--level' option to `doorstop add` to force an item level.
- Added warnings for duplicate item levels in a document.
- Added warnings for skipped item levels in a document.
- Renamed `Item` methods: add_link -> link, remove_link -> unlink, valid -> validate.
- Renamed `Document` methods: add -> add_item, remove -> remove_item, valid -> validate.
- Renamed `Tree` methods: new -> new_document, add -> add_item, remove -> remove_item, link -> link_items, unlink -> unlink_items, edit -> edit_item, valid -> validate.
- Added `doorstop.importer` functions to add exiting documents and items.

0.4.3 (2014/03/18)
------------------

- Fixed storage of 2-part levels ending in a multiple of 10.

0.4.2 (2014/03/17)
------------------

- Fixed a case where `Item.root` was not set.

0.4.1 (2014/03/16)
------------------

- Fixed auto save/load decorator order.

0.4 (2014/03/16)
----------------

- Added `Tree.delete()` to delete all document directories and item files.
- Added `doorstop publish all <directory>` to publish trees and `index.html`.

0.3 (2014/03/12)
----------------

- Added find_document and find_item convenience functions.
- Added `Document.delete()` to delete a document directory and its item files.

0.2 (2014/03/05)
----------------

- All `Item` text attributes are now be split by sentences and line-wrapped.
- Added `Tree.load()` for cases when lazy loading is too slow.
- Added caching to `Tree.find_item()` and `Tree.find_document()`.


0.1 (2014/02/17)
----------------

- Top-level items are no longer required to have a level ending in zero.
- Added `Item/Document.extended` to get a list of extended attribute names.


0.0.21 (2014/02/14)
-------------------

- Documents can now have item files in sub-folders.


0.0.20 (2014/02/13)
-------------------

- Updated `doorstop.core.report` to support lists of items.


0.0.19 (2014/02/13)
-------------------

- Updated doorstop.core.report to support items or documents.
- Removed the 'iter\_' prefix from all generators.


0.0.18 (2014/02/12)
-------------------

- Fixed CSS bullets indent.


0.0.17 (2014/01/31)
-------------------

- Added caching of `Item` in the `Document` class.
- Added `Document.remove()` to delete an item by its ID.
- `Item.find_rlinks()` will now search the entire tree for links.


0.0.16 (2014/01/28)
-------------------

- Added `Item.find_rlinks()` to return reverse links and child documents.
- Changed the logging format.
- Added a '--project' argument to provide a path to the root of the project.


0.0.15 (2014/01/27)
-------------------

- Fixed a mutable default argument bug in `Item` creation.


0.0.14 (2014/01/27)
-------------------

- Added `Tree/Document/Item.iter_issues()` method to yield all issues.
- `Tree/Document/Item.check()` now logs all issues rather than failing fast.
- Renamed `Tree/Document/Item.check()` to `valid()`.


0.0.13 (2014/01/25)
-------------------

- Added `Document.sep` to separate prefix and item numbers.


0.0.12 (2014/01/24)
-------------------

- Fixed missing package data.


0.0.11 (2014/01/23)
-------------------

- Added `Item.active` property to disable certain items.
- Added `Item.derived` property to disable link checking on certain items.


0.0.10 (2014/01/22)
-------------------

- Switched to embedded CSS in generated HTML.
- Shortened default `Item` and `Document` string formatting.


0.0.9 (2014/01/21)
------------------

- Added top-down link checking.
- Non-normative items with a zero-ended level are now headings.
- Added a CSS for generated HTML.
- The 'publish' command now accepts an output file path.


0.0.8 (2014/01/16)
------------------

- Searching for 'ref' will now also find filenames.
- Item files can now contain arbitrary fields.
- Document prefixes can now contain numbers, dashes, and periods.
- Added a 'normative' attribute to the Item class.


0.0.7 (2013/12/09)
------------------

- Always showing 'ref' in items.
- Reloading item attributes after a save.
- Inserting lines breaks after sentences in item 'text'.


0.0.6 (2013/12/04)
------------------

- Added basic report creation via `doorstop publish ...`.


0.0.5 (2013/11/20)
------------------

- Added item link and reference validation.
- Added cached of loaded items.
- Added preliminary VCS support for Git and Veracity.


0.0.4 (2013/11/04)
------------------

- Implemented `add`, `remove`, `link`, and `unlink` commands.
- Added basic tree validation.


0.0.3 (2013/10/17)
------------------

- Added the initial `Document` class.
- Items can now be ordered by 'level' in a document.
- Initial tutorial created.


0.0.2 (2013/09/25)
------------------

- Changed `doorstop init` to `doorstop new`.
- Added the initial `Item` class.
- Added stubs for the `Document` class.


0.0.1 (2013/09/11)
------------------

- Initial release of Doorstop.


