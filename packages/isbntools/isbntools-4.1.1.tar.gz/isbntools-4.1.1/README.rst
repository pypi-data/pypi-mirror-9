.. image:: https://pypip.in/d/isbntools/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/isbntools/
    :alt: Downloads

.. image:: https://pypip.in/v/isbntools/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/isbntools/
    :alt: Latest Version

.. image:: https://pypip.in/format/isbntools/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/isbntools/
    :alt: Download format

.. image:: https://pypip.in/py_versions/isbntools/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/isbntools/
    :alt: Python Versions

.. image:: https://pypip.in/license/isbntools/badge.svg?style=flat
    :target: https://pypi.python.org/pypi/isbntools/
    :alt: License

.. image:: https://readthedocs.org/projects/isbntools/badge/?version=latest
    :target: http://isbntools.readthedocs.org/en/latest/
    :alt: Documentation Status

.. image:: https://sourcegraph.com/api/repos/github.com/xlcnd/isbntools/badges/status.png
    :target: https://sourcegraph.com/github.com/xlcnd/isbntools
    :alt: Graph

.. image:: https://coveralls.io/repos/xlcnd/isbntools/badge.png?branch=v4.1.1
    :target: https://coveralls.io/r/xlcnd/isbntools?branch=v4.1.1
    :alt: Coverage

.. image:: https://travis-ci.org/xlcnd/isbntools.svg?branch=v4.1.1
    :target: https://travis-ci.org/xlcnd/isbntools
    :alt: Built Status

.. image:: https://ci.appveyor.com/api/projects/status/chdwjfamexdp97rt?svg=true
    :target: https://ci.appveyor.com/project/xlcnd/isbntools
    :alt: Windows Built Status


**WARNING**
===========

  **If you are updating from 4.0.1** please:

  Uninstall `isbntools` (``sudo pip uninstall isbntools``)
  and then **delete** all files ``isbntools*`` in your ``site-packages`` directory, including the folder
  ``isbntools``

  Then install `isbntools 4.0.2` (``sudo pip install isbntools``).

  **NOTE**: in Windows (or in OSX/Linux for an user install) you shouldn't use ``sudo pip ...``, just ``pip ...``


Info
====

``isbntools`` provides several useful methods and functions
to validate, clean, transform, hyphenate and
get metadata for ISBN strings.


**For the end user** several scripts are provided to use **from the command line**:

.. code-block:: bash

    $ to_isbn10 ISBN13

transforms an ISBN13 number to ISBN10.

.. code-block:: bash

    $ to_isbn13 ISBN10

transforms an ISBN10 number to ISBN13.

.. code-block:: bash

    $ isbn_info ISBN

gives you the *group identifier* of the ISBN.

.. code-block:: bash

    $ isbn_mask ISBN

*masks* (hyphenate) an ISBN (split it by identifiers).

.. code-block:: bash

    $ isbn_meta ISBN [wcat|goob|openl|isbndb|merge] [bibtex|msword|endnote|refworks|opf|json] [YOUR_APIKEY_TO_SERVICE]

gives you the main metadata associated with the ISBN, ``wcat`` uses **worldcat.org**
(**no key is needed**), ``goob`` uses the **Google Books service** (**no key is needed**),
``isbndb`` uses the **isbndb.com** service (**an api key is needed**),
``openl`` uses the **OpenLibrary.org** api (**no key is needed**), ``merge`` uses
a merged record of ``wcat`` and ``goob`` records (**no key is needed**) and
**is the default option** (you only have to enter, e.g. ``isbn_meta 9780321534965``).
You can get an API key for the *isbndb.com service* here_.  You can enter API keys and
set preferences in the file ``isbntools.conf`` in your
``$HOME\.isbntools`` directory (UNIX). For Windows, you should look at
``%APPDATA%/isbntools/isbntools.conf``. The output can be formatted as ``bibtex``,
``msword``, ``endnote``, ``refworks``, ``opf`` or ``json`` (BibJSON) bibliographic formats.


.. code-block:: bash

    $ isbn_editions ISBN

gives the collection of ISBNs that represent a given book (uses worldcat.org).

.. code-block:: bash

    $ isbn_validate ISBN

validates ISBN10 and ISBN13.

.. code-block:: bash

    $ ... | isbn_stdin_validate

to use with *posix pipes* (e.g. ``cat FILE_WITH_ISBNs | isbn_stdin_validate``).

    **TIP** Suppose you want to extract the ISBN of a pdf eboook (MYEBOOK.pdf).
    Install pdfminer_ and then enter in a command line::

    $ pdf2txt.py -m 5 MYEBOOK.pdf | isbn_stdin_validate


.. code-block:: bash

    $ isbn_from_words "words from title and author name"

a *fuzzy* script that returns the *most probable* ISBN from a set of words!
(You can verify the result with ``isbn_meta``)!


.. code-block:: bash

    $ isbn_goom "words from title and author name" [bibtex|msword|endnote|refworks|json]

a script that returns from **Google Books multiple references**.


.. code-block:: bash

    $ isbn_doi ISBN

returns the doi's ISBN-A code of a given ISBN.


.. code-block:: bash

    $ isbn_EAN13 ISBN

returns the EAN13 code of a given ISBN.


.. code-block:: bash

    $ isbn_ren FILENAME

renames (using metadata) files in the **current directory** that have ISBNs in their
filename (e.g. ``isbn_ren 1783559284_book.epub``, ``isbn_ren "*.pdf"``).

    Enter ``isbn_ren`` to see many other options.


.. code-block:: bash

    $ isbntools

writes version and copyright notice and **checks if there are updates**.

With

.. code-block:: bash

    $ isbn_repl

you will get a **REPL with history, autocompletion, fuzzy options,
redirection and access to the shell**.

Following is a typical session:

.. code-block:: bash

    $ isbn_repl

        Welcome to the isbntools 4.1.1 REPL.
        ** For help type 'help' or '?'
        ** To exit type 'exit' :)
        ** To run a shell command, type '!<shellcmnd>'

    isbn> ?

    Commands available (type ?<command> to get help):
    =================================================
    BIBFORMATS  PROVIDERS  doi       exit        help  meta       to_isbn13
    EAN13       audit      doitotex  from_words  info  shell      validate
    EOF         conf       editions  goom        mask  to_isbn10

    isbn> meta 9780156001311 tex
    @book{9780156001311,
         title = {The Name Of The Rose},
        author = {Umberto Eco},
          isbn = {9780156001311},
          year = {1994},
     publisher = {Harcourt Brace}
    }
    isbn> meta 9780156001311 tex >>myreferences.bib
    isbn> !ls
    myreferences.bib
    isbn> exit
    bye


**Within REPL many of the operations are faster.**

Many more scripts could be written with the ``isbntools`` and ``isbnlib`` library,
using the methods for extraction, cleaning, validation and standardization of ISBNs.

Just for fun, suppose I want the *most spoken about* book with certain words in his title.
For a *quick-and-dirty solution*, enter the following code in a file
and save it as ``isbn_tmsa_book.py``.

.. code-block:: python

    #!/usr/bin/env python
    import sys
    from isbntools.app import *

    query = sys.argv[1].replace(' ', '+')
    isbn = isbn_from_words(query)

    print("The ISBN of the most `spoken-about` book with this title is %s" % isbn)
    print("")
    print("... and the book is:")
    print("")
    print((meta(isbn)))

Then in a command line (in the same directory):

.. code-block:: bash

    $ python isbn_tmsa_book.py 'noise'

In my case I get::


    The ISBN of the most `spoken-about` book with this title is 9780143105985

    ... and the book is:

    {'Publisher': u'Penguin Books', 'Language': u'eng', 'Title': u'White noise',
    'Year': u'2009', 'ISBN-13': u'9780143105985', 'Authors': u'Don DeLillo ;
    introduction by Richard Powers.'}


Have fun!


Install
=======

From the command line enter (in some cases you have to precede the
command with ``sudo``):


.. code-block:: bash

    $ pip install isbntools

or:

.. code-block:: bash

    $ easy_install isbntools

or:

.. code-block:: bash

    $ pip install isbntools-4.1.1.tar.gz

(first you have to download the file!)

You should check if the install was successful, by enter:

.. code-block:: bash

    $ isbntools


Portable Version (Windows and Linux)
------------------------------------

If you are on a Windows or Linux system,
you can download a portable_ version that **doesn't need python** and gives you
access to the scripts. However, doesn't support add-ins or customization!



    **Instructions**:

    1. unzip the file and put the file ``isbn.exe`` in a folder.
    2. go to that folder and open a command line.
    3. run ``isbn help`` to get further instructions.



For Devs
========

If all you want is to add ``isbntools`` to the requirements of your project,
probably you will better served with isbnlib_, it implements the basic functionality
of ``isbntools`` without end user scripts and configuration files!

If you thing that that is not enough, please read_ at least this page of the documentation.

If you would like to contribute to the project please read the guidelines_.


Conf File
=========

You can enter API keys and set preferences in the file ``isbntools.conf`` in your
``$HOME/.isbntools`` directory (UNIX). For Windows, you should look at
``%APPDATA%/isbntools/isbntools.conf``
(**create these, directory and file, if don't exist** [Now just enter ``isbn_conf make``!]).
The file should look like:

.. code-block:: bash

    ...

    [MISC]
    REN_FORMAT={firstAuthorLastName}{year}_{title}_{isbn}
    DEBUG=False

    [SYS]
    SOCKETS_TIMEOUT=15
    THREADS_TIMEOUT=12

    [SERVICES]
    DEFAULT_SERVICE=merge
    VIAS_MERGE=serial

    [PLUGINS]

    ...


The values are self-explanatory!


    **NOTE** If you are running ``isbntools`` inside a virtual environment, the
    ``isbntools.conf`` file will be at the root of the environment.

The easier way to manipulate these files is by using the script ``isbn_conf``.
At a terminal enter:

.. code-block:: bash

   $ isbn_conf show

to see the current conf file.

This script has many options that allow a controlled editing of the conf file.
Just enter ``isbn_conf`` for help.



isbntools.contrib
=================

To get extra functionality, search_ pypi for packages starting with ``isbntools.contrib``.



Known Issues
============

1. The ``meta`` method and the ``isbn_meta`` script sometimes give a wrong result
   (this is due to errors on the chosen service), in alternative you could
   try one of the others services.

2. The ``isbntools`` works internally with unicode, however this doesn't
   solve errors of lost information due to bad encode/decode at the origin!

3. Periodically, agencies, issue new blocks of ISBNs. The
   range_ of these blocks is on a database that ``mask`` uses. So it could happen,
   if you have a version of ``isbntools`` that is too old, ``mask`` doesn't work for
   valid (recent) issued ISBNs. The solution? **Update isbntools often**!

4. Calls to metadata services are cached by default. If you don't want this
   feature, just enter ``isbn_conf setopt cache no``. If by any reason you need
   to clear the cache, just enter ``isbn_conf delcache``.

Any issue that you would like to report, (if you are a developer) please do it at github_
or at stackoverflow_ with tag **isbntools**,
(if you are an end user) at twitter_.


--------------------------------

.. class:: center

More documentation at Read the Docs_.

--------------------------------

.. _github: https://github.com/xlcnd/isbntools/issues

.. _range: https://www.isbn-international.org/range_file_generation

.. _here: http://isbndb.com/api/v2/docs

.. _read: http://isbntools.readthedocs.org/en/latest/devs.html

.. _guidelines: http://bit.ly/1jcxq8W

.. _portable: http://bit.ly/1i8qatY

.. _twitter: https://twitter.com/isbntools

.. _pdfminer: https://pypi.python.org/pypi/pdfminer

.. _isbnlib: http://bit.ly/ISBNlib

.. _search: https://pypi.python.org/pypi?%3Aaction=search&term=isbntools.contrib&submit=search

.. _Docs: http://bit.ly/1l0W4In

.. _stackoverflow: http://stackoverflow.com/questions/tagged/isbntools
