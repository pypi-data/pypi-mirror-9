[![Downloads](https://pypip.in/d/isbntools/badge.png)](https://pypi.python.org/pypi/isbntools/)
[![Latest Version](https://pypip.in/v/isbntools/badge.png)](https://pypi.python.org/pypi/isbntools/)
[![Download format](https://pypip.in/format/isbntools/badge.png)](https://pypi.python.org/pypi/isbntools/)
[![License](https://pypip.in/license/isbntools/badge.png)](https://pypi.python.org/pypi/isbntools/)
[![Coverage Status](https://coveralls.io/repos/xlcnd/isbntools/badge.png?branch=v3.3.9)](https://coveralls.io/r/xlcnd/isbntools?branch=v3.3.9)
[![Graph](https://sourcegraph.com/api/repos/github.com/xlcnd/isbntools/badges/status.png)](https://sourcegraph.com/github.com/xlcnd/isbntools)
[![Documentation Status](https://readthedocs.org/projects/isbntools/badge/?version=latest)](http://isbntools.readthedocs.org/en/latest/)
[![Build Status](https://travis-ci.org/xlcnd/isbntools.svg?branch=v3.3.9)](https://travis-ci.org/xlcnd/isbntools)


Info
----

`isbntools` provides several useful methods and functions
to validate, clean, transform, hyphenate and
get metadata for ISBN strings.

Typical usage (as library):

```python
#!/usr/bin/env python
import isbntools
    ...
```

**For the end user** several scripts are provided to use **from the command line**:

```bash
$ to_isbn10 ISBN13
```
transforms an ISBN13 number to ISBN10.

```bash
$ to_isbn13 ISBN10
```
transforms an ISBN10 number to ISBN13.

```bash
$ isbn_info ISBN
```
gives you the *group identifier* of the ISBN.

```bash
$ isbn_mask ISBN
```
*masks* (hyphenate) an ISBN (split it by identifiers).

```bash
$ isbn_meta ISBN [wcat|goob|openl|isbndb|merge] [bibtex|...] [YOUR_APIKEY_TO_SERVICE]
```
gives you the main metadata associated with the ISBN, `wcat` uses **worldcat.org**
(**no key is needed**), `goob` uses the **Google Books service** (**no key is needed**),
`isbndb` uses the **isbndb.com** service (**an api key is needed**),
`openl` uses the **OpenLibrary.org** api (**no key is needed**), `merge` uses
a merged record of `wcat` and `goob` records (**no key is needed**) and
**is the default option** (you only have to enter, e.g. `isbn_meta 9780321534965`).
You can get an API key for the *isbndb.com service* [here](http://isbndb.com/api/v2/docs).
You can enter API keys and set preferences in the file `isbntools.conf` in your
`$HOME\.isbntools` directory (UNIX). For Windows, you should look at
`%APPDATA%/isbntools/isbntools.conf`.
The output can be formatted as `bibtex`, `msword`,  `endnote`, `refworks`, `opf`, or
`json` (BibJSON) bibliographic formats.


```bash
$ isbn_editions ISBN
```
gives the collection of ISBNs that represent a given book (uses worldcat.org).

```bash
$ isbn_validate ISBN
```
validates ISBN10 and ISBN13.

```bash
$ ... | isbn_stdin_validate
```
to use with *pipes* (e.g. `cat FILE_WITH_ISBNs | isbn_stdin_validate`).

```bash
$ isbn_from_words "words from title and author name"
```
a *fuzzy* script that returns the *most probable* ISBN from a set of words.
(You can verify the result with `isbn_meta`)!

```bash
$ isbn_goom "words from title and author name" [bibtex|opf|msword|endnote|refworks|json]
```
a script that returns from **Google Books multiple references**.


```bash
$ isbn_doi ISBN
```
returns the doi's ISBN-A code of a given ISBN.


```bash
$ isbn_EAN13 ISBN
```
returns the EAN13 code of a given ISBN.

```bash
$ isbn_ren FILENAME
```
renames (using metadata) files in the **current directory** that have ISBNs in their
filename (e.g. `isbn_ren 1783559284_book.epub`, `isbn_ren "*.pdf"`).

>Enter `isbn_ren` to see many other options.

```bash
$ isbntools
```
writes version and copyright notice and **checks if there are updates**.

Many more scripts could be written with the `isbntools` library,
using the methods for extraction, cleaning, validation and standardization of ISBNs.

Just for fun, suppose I want the *most spoken about* book with certain words in his title.
For a *quick-and-dirty solution*, enter the following code in a file
and save it as `isbn_tmsa_book.py`.

```python
#!/usr/bin/env python
import sys
from isbntools import *

query = sys.argv[1].replace(' ', '+')
isbn = isbn_from_words(query)

print("The ISBN of the most `spoken-about` book with this title is %s" % isbn)
print("")
print("... and the book is:")
print("")
print((meta(isbn)))
```

Then in a command line (in the same directory):

```bash
$ python isbn_tmsa_book.py 'noise'
```

In my case I get:

```
The ISBN of the most `spoken-about` book with this title is 9780143105985

... and the book is:

{'Publisher': u'Penguin Books', 'Language': u'eng', 'Title': u'White noise',
'Year': u'2009', 'ISBN-13': u'9780143105985', 'Authors': u'Don DeLillo ;
introduction by Richard Powers.'}
```

Have fun!

Install
-------

From the command line enter (in some cases you have to preced the
command with `sudo`):

```bash
$ pip install isbntools
```
this installs from [pypi](https://pypi.python.org/pypi/isbntools) or:

```bash
$ easy_install isbntools
```
this installs from [pypi](https://pypi.python.org/pypi/isbntools) too, or (to install locally in *Linux* or *Mac OS X*):

```bash
$ pip install isbntools-3.3.9.tar.gz
```
but first you have to [download](https://pypi.python.org/packages/source/i/isbntools/isbntools-3.3.9.tar.gz) the file!


You should check if the install was successful, by enter:

```bash
$ isbntools
```


### Windows (NOW for Linux too!)

>**If you are on a Windows system (NOW for Linux too)**,
you can download a
[standalone version](http://bit.ly/1i8qatY)
that **doesn't need python** and gives you
access to the scripts. However, doesn't support add-ins or customization!

>**Instructions**:
1. unzip the file and put the file `isbn.exe` in a folder
2. go to that folder and open a command line
3. run `isbn help` to get further instructions


For Devs
--------

If all you want is to add `isbntools` to the requirements of your project,
probably you will better served with [isbnlib](http://bit.ly/ISBNlib),
it implements the basic functionality
of `isbntools` without end user scripts and configuration files!

If you thing that that is not enough,
please read at least [this page of the documentation](http://isbntools.readthedocs.org/en/latest/devs.html).

If you would like to contribute to the project please read the [guidelines](http://bit.ly/1jcxq8W).


Conf File
---------

You can enter API keys and set preferences in the file `isbntools.conf` in your
`$HOME\.isbntools` directory (UNIX). For Windows, you should look at
`%APPDATA%/isbntools/isbntools.conf`
(**create these, directory and file, if don't exist** [Now, just enter `isbn_conf make`]).
The file should look like:

```bash
...

[SYS]
SOCKETS_TIMEOUT=15
THREADS_TIMEOUT=12

[SERVICES]
DEFAULT_SERVICE=merge
VIAS_MERGE=serial
ISBNDB_API_KEY=your_api_key_here_or_DELETEME

[PLUGINS]
isbndb=isbndb.py
openl=openl.py

...
```

The values are self-explanatory!


> **NOTE** If you are running `isbntools` inside a virtual environment, the
`isbntools.conf` file will be at the root of the environment.

The easier way to manipulate these files is by using the script `isbn_conf`.
At a terminal enter:

```bash
$ isbn_conf show
```

to see the current conf file.

This script has many options that allow a controlled editing of the conf file.
Just enter `isbn_conf` for help.



isbntools.contrib
-----------------

To get extra functionality, 
[search pypi](https://pypi.python.org/pypi?%3Aaction=search&term=isbntools.contrib&submit=search)
for packages starting with ``isbntools.contrib``.



Known Issues
------------

1. The `meta` method and the `isbn_meta` script sometimes give a wrong result
   (this is due to errors on the chosen service), in alternative you could
   try one of the others services.

2. The `isbntools` works internally with unicode, however this doesn't
   solve errors of lost information due to bad encode/decode at the origin!

3. Periodically, agencies, issue new blocks of ISBNs. The
   [*range*](https://www.isbn-international.org/range_file_generation) of
   these blocks is on a database that `mask` uses. So it could happen, if you
   have a version of `isbntools` that is too old, `mask` doesn't work for
   valid (recent) issued ISBNs. The solution? **Update `isbntools` often**!

4. Calls to metadata services are cached by default. If you don't want this
   feature, just enter `isbn_conf setopt cache no`. If by any reason you need
   to clear the cache, just enter `isbn_conf delcache`.

Any issue that you would like to report, please do it at
[github](https://github.com/xlcnd/isbntools/issues) (if you are a developer)
or at [twitter](https://twitter.com/isbntools) (if you are an end user).



---
More documentation at [isbntools.readthedocs.org](http://bit.ly/1l0W4In)
