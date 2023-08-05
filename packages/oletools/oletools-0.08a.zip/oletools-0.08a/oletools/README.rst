python-oletools
===============

`python-oletools <http://www.decalage.info/python/oletools>`_ is a
package of python tools to analyze `Microsoft OLE2
files <http://en.wikipedia.org/wiki/Compound_File_Binary_Format>`_ (also
called Structured Storage, Compound File Binary Format or Compound
Document File Format), such as Microsoft Office documents or Outlook
messages, mainly for malware analysis, forensics and debugging. It is
based on the `olefile <http://www.decalage.info/olefile>`_ parser. See
`http://www.decalage.info/python/oletools <http://www.decalage.info/python/oletools>`_
for more info.

**Quick links:** `Home page <http://www.decalage.info/python/oletools>`_
-
`Download/Install <https://bitbucket.org/decalage/oletools/wiki/Install>`_
- `Documentation <https://bitbucket.org/decalage/oletools/wiki>`_ -
`Report
Issues/Suggestions/Questions <https://bitbucket.org/decalage/oletools/issues?status=new&status=open>`_
- `Contact the Author <http://decalage.info/contact>`_ -
`Repository <https://bitbucket.org/decalage/oletools>`_ - `Updates on
Twitter <https://twitter.com/decalage2>`_

Note: python-oletools is not related to OLETools published by BeCubed
Software.

News
----

-  **2015-01-05 v0.07**: improved
   `olevba <https://bitbucket.org/decalage/oletools/wiki/olevba>`_ to
   detect suspicious keywords and IOCs in VBA macros, can now scan
   several files and open password-protected zip archives, added a
   Python API, upgraded OleFileIO\_PL to olefile v0.41
-  2014-08-28 v0.06: added
   `olevba <https://bitbucket.org/decalage/oletools/wiki/olevba>`_, a
   new tool to extract VBA Macro source code from MS Office documents
   (97-2003 and 2007+). Improved
   `documentation <https://bitbucket.org/decalage/oletools/wiki>`_
-  2013-07-24 v0.05: added new tools
   `olemeta <https://bitbucket.org/decalage/oletools/wiki/olemeta>`_ and
   `oletimes <https://bitbucket.org/decalage/oletools/wiki/oletimes>`_
-  2013-04-18 v0.04: fixed bug in rtfobj, added documentation for
   `rtfobj <https://bitbucket.org/decalage/oletools/wiki/rtfobj>`_
-  2012-11-09 v0.03: Improved
   `pyxswf <https://bitbucket.org/decalage/oletools/wiki/pyxswf>`_ to
   extract Flash objects from RTF
-  2012-10-29 v0.02: Added
   `oleid <https://bitbucket.org/decalage/oletools/wiki/oleid>`_
-  2012-10-09 v0.01: Initial version of
   `olebrowse <https://bitbucket.org/decalage/oletools/wiki/olebrowse>`_
   and pyxswf
-  see changelog in source code for more info.

Tools in python-oletools:
-------------------------

-  `olebrowse <https://bitbucket.org/decalage/oletools/wiki/olebrowse>`_:
   A simple GUI to browse OLE files (e.g. MS Word, Excel, Powerpoint
   documents), to view and extract individual data streams.
-  `oleid <https://bitbucket.org/decalage/oletools/wiki/oleid>`_: a tool
   to analyze OLE files to detect specific characteristics usually found
   in malicious files.
-  `olemeta <https://bitbucket.org/decalage/oletools/wiki/olemeta>`_: a
   tool to extract all standard properties (metadata) from OLE files.
-  `oletimes <https://bitbucket.org/decalage/oletools/wiki/oletimes>`_:
   a tool to extract creation and modification timestamps of all streams
   and storages.
-  `olevba <https://bitbucket.org/decalage/oletools/wiki/olevba>`_: a
   tool to extract and analyze VBA Macro source code from MS Office
   documents (OLE and OpenXML).
-  `pyxswf <https://bitbucket.org/decalage/oletools/wiki/pyxswf>`_: a
   tool to detect, extract and analyze Flash objects (SWF) that may be
   embedded in files such as MS Office documents (e.g. Word, Excel) and
   RTF, which is especially useful for malware analysis.
-  `rtfobj <https://bitbucket.org/decalage/oletools/wiki/rtfobj>`_: a
   tool and python module to extract embedded objects from RTF files.
-  and a few others (coming soon)

Download and Install:
---------------------

To use python-oletools from the command line as analysis tools, you may
simply `download the zip
archive <https://bitbucket.org/decalage/oletools/downloads>`_ and
extract the files in the directory of your choice.

To get the latest development version, click on "Download repository" on
the `downloads
page <https://bitbucket.org/decalage/oletools/downloads>`_, or use
mercurial to clone the repository.

If you plan to use python-oletools with other Python applications or
your own scripts, then the simplest solution is to use "**pip install
oletools**\ " or "**easy\_install oletools**\ " to download and install
in one go. Otherwise you may download/extract the zip archive and run
"**setup.py install**\ ".

Documentation:
--------------

The latest version of the documentation can be found
`online <https://bitbucket.org/decalage/oletools/wiki>`_, otherwise a
copy is provided in the doc subfolder of the package.

How to Suggest Improvements, Report Issues or Contribute:
---------------------------------------------------------

This is a personal open-source project, developed on my spare time. Any
contribution, suggestion, feedback or bug report is welcome.

To suggest improvements, report a bug or any issue, please use the
`issue reporting
page <https://bitbucket.org/decalage/olefileio_pl/issues?status=new&status=open>`_,
providing all the information and files to reproduce the problem.

You may also `contact the author <http://decalage.info/contact>`_
directly to provide feedback.

The code is available in `a Mercurial repository on
Bitbucket <https://bitbucket.org/decalage/oletools>`_. You may use it to
submit enhancements using forks and pull requests.

License
-------

This license applies to the python-oletools package, apart from the
thirdparty folder which contains third-party files published with their
own license.

The python-oletools package is copyright (c) 2012-2015 Philippe Lagadec
(http://www.decalage.info)

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

-  Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.
-  Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

--------------

olevba contains modified source code from the officeparser project,
published under the following MIT License (MIT):

officeparser is copyright (c) 2014 John William Davison

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
