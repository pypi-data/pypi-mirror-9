What is lingua?
===============

Lingua is a package with tools to extract translatable texts from
your code, and to check existing translations. It replaces the use
of the ``xgettext`` command from gettext, or ``pybabel`` from Babel.


Message extraction
==================

The simplest way to extract all translatable messages is to point the
``pot-create`` tool at the root of your source tree.

::

     $ pot-create src

This will create a ``messages.pot`` file containing all found messages.


Specifying input files
----------------------

There are three ways to tell lingua which files you want it to scan:

1. Specify filenames directly on the command line. For example::

   $ pot-create main.py utils.py

2. Specify a directory on the command line. Lingua will recursively scan that
   directory for all files it knows how to handle.

   ::

       $ pot-create src

3. Use the ``--files-from`` parameter to point to a file with a list of
   files to scan. Lines starting with ``#`` and empty lines will be ignored.

   ::

       $ pot-create --files-from=POTFILES.in

You can also use the ``--directory=PATH`` parameter to add the given path to the
list of directories to check for files. This may sound confusing, but can be
useful. For example this command will look for ``main.py`` and ``utils.py`` in
the current directory, and if they are not found there in the ``../src``
directory::


    $ pot-create --directory=../src main.py utils.py


Configuration
-------------

In its default configuration lingua will use its python extractor for ``.py``
files, its XML extractor for ``.pt`` and ``.zpt`` files and its ZCML extractor
for ``.zcml`` files. If you use different extensions you setup a configuration
file which tells lingua how to process files. This file uses a simple ini-style
format.

There are two types of configuration that can be set in the configuration file:
which extractor to use for a file extension, and the configuration for a single
extractor.

File extensions are configured in the ``extensions`` section. Each entry in
this section maps a file extension to an extractor name. For example to
tell lingua to use its XML extractor for files with a ``.html`` extension
you can use this configuration::

    [extensions]
    .html = xml

To find out which extractors are available use the ``-list-extractors`` option.

::

    $ bin/pot-create --list-extractors
    chameleon         Chameleon templates (defaults to Python expressions)
    python            Python sources
    xml               Chameleon templates (defaults to Python expressions)
    zcml              Zope Configuration Markup Language (ZCML)
    zope              Zope templates (defaults to TALES expressions)

A section named `extractor:<name>` can be used to configure a specific
extractor. For example to tell the XML extractor that the default language
used for expressions is TALES instead of Python::

    [extractor:xml]
    default-engine = tales

Either place a global configuration file named ``.config/lingua`` to your
home folder or use the ``--config`` option to point lingua to your
configuration file.

::

    $ pot-create -c lingua.cfg src


Domain filtering
----------------

When working with large systems you may use multiple translation domains
in a single source tree. Lingua can support that by filtering messages by
domain when scanning sources. To enable domain filtering use the ``-d`` option:

::

    $ pot-create -d mydomain src

Lingua will always include messages for which it can not determine the domain.
For example, take this Python code:

::

     print(gettext(u'Hello, World'))
     print(dgettext('mydomain', u'Bye bye'))

The first hello-message does not specify its domain and will always be
included. The second line uses `dgettext
<http://docs.python.org/2/library/gettext#gettext.dgettext>`_ to explicitly
specify the domain. Lingua will use this information when filtering domains.


Specifying keywords
-------------------

When looking for messages a lingua parser uses a default list of keywords
to identify translation calls. You can add extra keywords via the ``--keyword``
option. If you have your own ``mygettext`` function which takes a string
to translate as its first parameter you can use this:

::

    $ pot-create --keyword=mygettext

If your function takes more parameters you will need to tell lingua about them.
This can be done in several ways:

* If the translatable text is not the first parameter you can specify the
  parameter number with ``<keyword>:<parameter number>``. For example if
  you use ``i18n_log(level, msg)`` the keyword specifier would be ``i18n_log:2``
* If you support plurals you can specify the parameter used for the plural message
  by specifying the parameter number for both the singular and plural text. For
  example if your function signature is ``show_result(single, plural)`` the
  keyword specifier is ``show_result:1,2``
* If you use message contexts you can specify the parameter used for the context
  by adding a ``c`` to the parameter number. For example the keyword specifier for
  ``pgettext`` is ``pgettext:1c,2``.
* If your function takes the domain as a parameter you can specify which parameter
  is used for the domain by adding a ``d`` to the parameter number. For example
  the keyword specifier for ``dgettext`` is ``dgettext:1d,2``. This is a
  lingua-specified extension.
* You can specify the exact number of parameters a function call must have
  using the ``t`` postfix. For example if a function *must* have four parameters
  to be a valid call, the specifier could be ``myfunc:1,4t``.


Extractors
==========

Lingua includes a number of extractors:

* `python`: handles Python source code.
* `chameleon`: handles `Chameleon <http://www.pagetemplates.org/>`_ files,
  using the `Zope i18n syntax
  <https://chameleon.readthedocs.org/en/latest/reference.html#id51>`_
* `zcml`: handles Zope Configuration Markup Language (ZCML) files.
* `zope`: a variant of the chameleon extractor, which assumes the default
   expression language is `TALES
   <https://chameleon.readthedocs.org/en/latest/reference.html#expressions-tales>`_
   instead of Python.
* `xml`: old name for the `chameleon` extractor. This should not be used
   anymore.

Babel extractors
----------------

There are several packages with plugins for `Babel
<http://babel.edgewall.org/>`_'s message extraction tool. Lingua can use those
plugins as well. The plugin names will be prefixed with ``babel-`` to
distinguish them from lingua extractors.

For example, if you have the `PyBabel-json
<https://pypi.python.org/pypi/PyBabel-json>`_ package installed you can
instruct lingua to use it for .json files by adding this to your configuration
file::

     [extensions]
     .json = babel-json

Some Babel plugins require you to specify comment tags. This can be set with
the ``comment-tags`` option.

::

    [extractor:babel-mako]
    comment-tags = TRANSLATOR:


Comparison to other tools
=========================

Differences compared to `GNU gettext <https://www.gnu.org/software/gettext/>`_:

* Support for file formats such as Zope Page Templates (popular in
  `Pyramid <http://docs.pylonsproject.org/projects/pyramid/en/latest/>`_,
  `Chameleon`_,
  `Plone <http://plone.org/>`_ and `Zope <http://www.zope.org>`_).
* Better support for detecting format strings used in Python.
* No direct support for C, C++, Perl, and many other languages. Lingua focuses
  on languages commonly used in Python projects, although support for other
  languages can be added via plugins.


Differences compared to `Babel`_:

* More reliable detection of Python format strings.
* Lingua includes plural support.
* Support for only extracting texts for a given translation domain. This is
  often useful for extensible software where you use multiple translation
  domains in a single application.


Validating translations
=======================

Lingua includes a simple ``polint`` tool which performs a few basic checks on
PO files. Currently implemented tests are:

* duplicated message ids (can also be checked with GNU gettext's ``msgfmt``).
  These should never happen and are usually a result of a bug in the message
  extraction logic.

* identical translations used for multiple canonical texts. This can happen
  for valid reasons, for example when the original text is not spelled
  consistently.

To check a po file simply run ``polint`` with the po file as argument::

    $ polint nl.po

    Translation:
        ${val} ist keine Zeichenkette
    Used for 2 canonical texts:
    1       ${val} is not a string
    2       "${val}" is not a string


Writing custom extractors
=========================

First we need to create the custom extractor::

    from lingua.extractors import Extractor
    from lingua.extractors import Message

    class MyExtractor(Extractor):
        '''One-line description for --list-extractors'''
        extensions = ['.txt']

        def __call__(self, filename, options):
            return [Message(None, 'msgid', None, [], u'', u'', (filename, 1))]

Hooking up extractors to lingua is done by ``lingua.extractors`` entry points
in ``setup.py``::

    setup(name='mypackage',
          ...
          install_requires=[
              'lingua',
          ],
          ...
          entry_points='''
          [lingua.extractors]
          my_extractor = mypackage.extractor:MyExtractor
          '''
          ...)

Note - the registered extractor must be a class derived from the ``Extractor``
base class.

After installing ``mypackage`` lingua will automatically detect the new custom
extractor.


Helper Script
=============

There exists a helper shell script for managing translations of packages in
``docs/examples`` named ``i18n.sh``. Copy it to package root where you want to
work on translations, edit the configuration params inside the script and use::

    ./i18n.sh lang

for initial catalog creation and::

    ./i18n.sh

for updating translation and compiling the catalog.

Changelog
=========

3.8 - January 20, 2015
----------------------

- Add options to sort messages by either location or message id when creating a
  POT file.


3.7 - December 17, 2014
-----------------------

- Include used lingua version in POT metadata.

- Add support for message contexts in translationstring instances.

- Add support for i18n:comment attributes in ZPT templates.


3.6.1 - November 11, 2014
-------------------------

- Restore Python 2.6 compatibility.


3.6 - November 11, 2014
-----------------------

- Extend automatic context-comments for ZPT templates to also show the
  canonical text for sub-elements.  For example this markup::

     <p i18n:translate="">This is just
       <em i18n:name="wonderful" i18n:translate="">wonderful</em>!</p>

  The resulting PO entry for the outer element will look like this::

    #. Canonical text for ${wonderful} is: "wonderful"
    msgid "This is just ${wonderful}!"
    msgstr ""

  This is only do for sub-elements that have a name (i.e. the have an
  ``i18n:name`` attribute).


3.5.1 - November 11, 2014
-------------------------

- Fix a bug in the generated context-comment for substrings which
  caused part of the outer sentence text to be skipped.

3.5 - November 11, 2014
-----------------------

- When encountering nested translations in ZPT templates automatically add a
  comment to the sub-message with the full text for the outer sentence. For
  example this markup::

     <p i18n:translate="">This is just
       <em i18n:name="wonderful" i18n:translate="">wonderful</em>!</p>

  The resulting PO entry will look like this::

    #. Used in sentence: "This is just ${wonderful}!"
    msgid "wonderful"
    msgstr ""

  This extra context information can be very important for translators.


3.4 - November 3, 2014
----------------------

- Add support for the ``i18n:context`` attribute in ZPT templates. This is
  supported by Chameleon 2.17 and later to set the translation context.


3.3 - September 14, 2014
------------------------

- Modify the message format-checker to not consider a space ofter a percent-
  character as a format flag. Space is a valid flag but is almost never used,
  and this was creating a lot of false positives (for example a sentence like
  "take a sample of 5% of all candidates").

- Do not try to extract a message from ``N_()`` calls: these are explicitly
  intended to be used for situations where you pass in a variable instead of
  a string.


3.2 - August 26, 2014
---------------------

- Refactor the extractor API a little bit to make it easier for extractors
  to call each other. This is particularly useful when an extractor needs to
  call the Python extractor to handle local Python expressions.

- Correctly extract messages from empty elements that used HTML notation. This
  fixes `issue 48 <https://github.com/wichert/lingua/issues/48>`_.


3.1 - August 18, 2014
---------------------

- Make sure two message strings are added when a plural message is encountered.
  This fixes an error from `msginit` when it sees ``msgid_plural`` but only a
  single ``msgstr``


3.0 - August 15, 2014
---------------------

*Zope users*: this release changes the extraction for `.pt` files. You will
need to configure lingua to use the new ``zope`` extractor for ``.pt`` files.

- Make it possible to configure Babel plugins.

- Include a brief description in ``--list-extractors`` output.

- Rename the ``xml`` extractor to ``chameleon`` to better fit the syntax it
  handles.

- Add a new ``zope`` extractor. This is identical to the chameleon extractor,
  but changes the default expression engine used to TALES. This engine is now
  the default for ``.cpt`` and ``.zpt`` files.

- Allow per-extractor configuration.

- Fix handling of comments returned by Babel extractor plugins. This fixes
  `issue 44 <https://github.com/wichert/lingua/issues/44>`_.


2.5 - August 14, 2014
---------------------

- Correct handling of alternatives in TALES expressions when the pipe-symbol
  was surrounded by whitespace. This fixes
  `issue 43 <https://github.com/wichert/lingua/issues/43>`_.

- Extractors can now be hooked up from outside via entry points.

- Introduce ``lingua.extractors.Extractor`` object and use it as base for
  all extractors.

- Check for global ``.config/lingua`` config file in user's home directory if
  no explicit config file defined.

- Fix error message when detecting a syntax error in scanned Python code. Patch
  from tisdall (`pull request 42
  <https://github.com/wichert/lingua/pull/42>`_).

- Use a single wheel distrbution for Python 2 and Python 3.


2.4 - July 23, 2014
-------------------

- Correctly handle multiple alternatives in ZPT expressions. This fixes
  `issue 39 <https://github.com/wichert/lingua/issues/39>`_.

- Do not add ``c-format`` flag for messages without an percent-character.

- Fix timezone format at pot creation (remove colon).


2.3 - June 13, 2014
-------------------

- Fix incorrect invocation of legacy Babel extraction plugins. This fixes
  `issue 28 <https://github.com/wichert/lingua/issues/28>`_.

- TAL template handling fixes:

  - Correctly handle ``structure:`` prefixes in TAL expressions. Patch from
    Ingmar Steen
    (`pull request 32 <https://github.com/wichert/lingua/pull/32>`_).

  - Fix handling of multi-line ``tal:content``, ``tal:define`` and ``tal:replace``
    statements. Patch from Ingmar Steen
    (pull requests
    `35 <https://github.com/wichert/lingua/pull/35>`_ and
    `36 <https://github.com/wichert/lingua/pull/36>`_).

  - Fix handling of ``tal:repeat`` statements with multiple assignments. Patch
    from Ingmar Steen
    (`pull request 37 <https://github.com/wichert/lingua/pull/37>`_).


2.2 - June 10, 2014
-------------------

- Remove seconds from POT timestamps. No other tool includes seconds, and this
  appearently breaks Babel.

- Fix Python 2.6 compatibility. Patch from Hugo Branquinho
  (`pull request 25 <https://github.com/wichert/lingua/pull/25>`_).

- Fix installation problems on Python 3. Patch from William Wu
  (`pull request 27 <https://github.com/wichert/lingua/pull/27>`_).

- Handle TALES expression engine selection. This fixes
  `issue 30 <https://github.com/wichert/lingua/issues/30>`_.

- Handle Python expressions using curly braces in HTML templates. This fixes
  `issue 29 <https://github.com/wichert/lingua/issues/29>`_.


2.1 - April 8, 2014
-------------------

- Do not break when encountering HTML entities in Python expressions in XML
  templates.

- Show the correct linenumber in error messages for syntax errors in Python
  expressions occurring in XML templates.

- Fix bug in parsing of ``tal:repeat`` and ``tal:define`` attributes in the
  XML parser.

- Tweak ReST-usage in changelog so the package documentation renders correctly
  on PyPI.


2.0 - April 8, 2014
-------------------

- Lingua is now fully Python 3 compatible.

- Add a new ``pot-create`` command to extract translateable texts. This is
  (almost) a drop-in replacement for GNU gettext's ``xgettext`` command and
  replaces the use of Babel's extraction tools. For backwards compatibility
  this tool can use existing Babel extraction plugins.

- Define a new extraction plugin API which enables several improvements to
  be made:

  - You can now select which domain to extract from files. This is currently
    only supported by the XML and ZCML extractors.
  - Format strings checks are now handled by the extraction plugin instead of
    applied globally. This prevents false positives.
  - Message contexts are fully supported.

- Format string detection has been improved: both C and Python format strings
  are now handled correctly.

- The XML/HTML extractor has been rewritten to use HTML parser from Chameleon_.
  This allows lingua to handle HTML files that are not valid XML.

- Whitespace handling in XML extractor has been improved..

- The po-xls conversion tools have been moved to a new `po-xls
  <https://github.com/wichert/po-xls>`_ package.


1.6 - December 9, 2013
----------------------

- Add support for ngettext and pluralize() for correctly generating plurals in
  pot files.


1.5 - April 1, 2013
-------------------

- Do not silently ignore XML parsing errors. Instead print an error message
  and abort.


1.4 - February 11, 2013
-----------------------

- Po->XLS convertor accidentily included obsolete messages.


1.3 - January 28, 2012
----------------------

- XLS->Po conversion failed for the first language if no comment or
  reference columns were generated. Reported by Rocky Feng.

- Properly support Windows in the xls-po convertors: Windows does not
  support atomic file renames, so revert to shutils.rename on that
  platform. Reported by Rocky Feng.


1.2 - January 13, 2012
----------------------

- Extend XML extractor to check python expressions in templates. This
  fixes `issue 7 <https://github.com/wichert/lingua/pull/7>`_. Thanks to
  Nuno Teixeira for the patch.


1.1 - November 16, 2011
-----------------------

- Set 'i18n' attribute as default prefix where there was no prefix found.
  This fixes issues `5 <https://github.com/wichert/lingua/issues/5>`_ and
  `6 <https://github.com/wichert/lingua/issues/5>`_. Thanks to
  Mathieu Le Marec - Pasquet for the patch.


1.0 - September 8, 2011
-----------------------

- Update XML extractor to ignore elements which only contain a Chameleon
  expression (``${....}``). These can happen to give the template engine
  a hint that it should try to translate the result of an expression. This
  fixes `issue 2 <https://github.com/wichert/lingua/issues/2>`_.

* Update XML extractor to not abort when encountering undeclared
  namespaces. This fixes `issue 3
  <https://github.com/wichert/lingua/issues/3>`_.

* Fix Python extractor to handle strings split over multiple lines
  correctly.


1.0b4 - July 20, 2011
---------------------

* Fix po-to-xls when including multiple languages in a single xls file.


1.0b3 - July 18, 2011
---------------------

* Paper brown bag: remove debug leftover which broke po-to-xls.


1.0b2 - July 18, 2011
---------------------

* Update PO-XLS convertors to allow selection of comments to include in
  the xls files.

* Correct XML extractor to strip leading and trailing white. This fixes
  `issue 1 <https://github.com/wichert/lingua/issues/1>`_.

* Add a very minimal polint tool to perform sanity checks in PO files.

* Update trove data: Python 2.4 is not supported due to lack of absolute
  import ability.


1.0b1 - May 13, 2011
--------------------

* First release.


