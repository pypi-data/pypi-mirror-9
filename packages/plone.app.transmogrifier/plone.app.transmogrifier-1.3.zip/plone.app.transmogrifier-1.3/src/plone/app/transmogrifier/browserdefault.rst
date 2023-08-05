Browser default section
-----------------------

A browser default pipeline section sets the default-page on a folder, and the
layout template on content objects. They are the Transmogrifier equivalent of
the ``display`` menu in Plone. The browser default section blueprint name is
``plone.app.transmogrifier.browserdefault``. Browser default sections operate
on objects already present in the ZODB, be they created by a constructor or 
pre-existing objects.

Setting the browser default needs at least 1 piece of information: the path to
the object to modify. To determine the path, the browser default section
inspects each item and looks for one key, as described below. Any item missing
this piece of information will be skipped. Similarly, items with a path that
doesn't exist or do not support the Plone ISelectableBrowserDefault interface
will be skipped as well.

For the object path, it'll look (in order) for
``_plone.app.transmogrifier.browserdefault_[sectionname]_path``,
``_plone.app.transmogrifier.browserdefault_path``, ``_[sectionname]_path``
and ``_path``, where ``[sectionname]`` is replaced with the name given to the
current section. This allows you to target the right section precisely if
needed. Alternatively, you can specify what key to use for the path by
specifying the ``path-key`` option, which should be a list of keys to try (one
key per line, use a ``re:`` or ``regexp:`` prefix to specify regular
expressions).

Once an object has been located, the section will looks for defaultpage
and layout keys. Like the path key, these can be specified in the source
configuration, named by the ``default-page-key`` and ``layout-key`` options,
respectively, and like the path key, the default keys the section looks for
are the usual list of specific-to-generic keys based on blueprint and section
names, from 
``_plone.app.transmogrifier.browserdefault_[sectionname]_defaultpage`` and
``_plone.app.transmogrifier.browserdefault_[sectionname]_layout`` down to
``_defaultpage`` and ``_layout``.

The defaultpage key will set the id of the default page that should be 
presented when the content object is loaded, and the layout key will set the
id of the layout to use for the content item.

::

    >>> import pprint
    >>> browserdefault = """
    ... [transmogrifier]
    ... pipeline =
    ...     browserdefaultsource
    ...     browserdefault
    ...     printer
    ...     
    ... [browserdefaultsource]
    ... blueprint = plone.app.transmogrifier.tests.browserdefaultsource
    ... 
    ... [browserdefault]
    ... blueprint = plone.app.transmogrifier.browserdefault
    ... 
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.browserdefault',
    ...                browserdefault)
    >>> transmogrifier(u'plone.app.transmogrifier.tests.browserdefault')
    >>> print(handler)
    logger INFO
      {'_layout': 'spam', '_path': '/spam/eggs/foo'}
    logger INFO
      {'_defaultpage': 'eggs', '_path': '/spam/eggs/bar'}
    logger INFO
      {'_defaultpage': 'eggs', '_layout': 'spam', '_path': '/spam/eggs/baz'}
    logger INFO
        {'_layout': 'spam',
       '_path': 'not/existing/bar',
       'title': 'Should not be updated, not an existing path'}
    logger INFO
        {'_path': 'spam/eggs/incomplete',
       'title': 'Should not be updated, no layout or defaultpage'}
    logger INFO
        {'_layout': '',
       '_path': 'spam/eggs/emptylayout',
       'title': 'Should not be updated, no layout or defaultpage'}
    logger INFO
        {'_defaultpage': '',
       '_path': 'spam/eggs/emptydefaultpage',
       'title': 'Should not be updated, no layout or defaultpage'}
    >>> pprint.pprint(plone.updated)
    [('spam/eggs/foo', 'layout', 'spam'),
     ('spam/eggs/bar', 'defaultpage', 'eggs'),
     ('spam/eggs/baz', 'layout', 'spam'),
     ('spam/eggs/baz', 'defaultpage', 'eggs')]
