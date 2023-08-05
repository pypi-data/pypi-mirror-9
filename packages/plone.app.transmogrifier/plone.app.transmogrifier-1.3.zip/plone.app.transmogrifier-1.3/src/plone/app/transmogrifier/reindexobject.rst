Indexing section
----------------

A ReindexObject section allows you to reindex an existing object in the
portal_catalog. ReindexObject sections operate on objects already present in the
ZODB, be they created by a constructor or pre-existing objects.

The ReindexObject blueprint name is ``plone.app.transmogrifier.reindexobject``.

To determine the path, the ReindexObject section inspects each item and looks
for a path key, as described below. Any item missing this key will be skipped.
Similarly, items with a path that doesn't exist or are not referenceable
(Archetypes) or do not inherit from CMFCatalogAware will be skipped as well.

The object path will be found under the first key found among the following:

* ``_plone.app.transmogrifier.reindexobject_[sectionname]_path``
* ``_plone.app.transmogrifier.reindexobject_path``
* ``_[sectionname]_path``
* ``_path``

where ``[sectionname]`` is replaced with the name given to the current section.
This allows you to target the right section precisely if needed.

Alternatively, you can specify what key to use for the path by specifying the
``path-key`` option, which should be a list of keys to try (one key per line;
use a ``re:`` or ``regexp:`` prefix to specify regular expressions).

Paths to objects are always interpreted as relative to the context.

::

    >>> import pprint
    >>> reindexobject = """
    ... [transmogrifier]
    ... pipeline =
    ...     reindexobjectsource
    ...     reindexobject
    ...     printer
    ...
    ... [reindexobjectsource]
    ... blueprint = plone.app.transmogrifier.tests.reindexobjectsource
    ...
    ... [reindexobject]
    ... blueprint = plone.app.transmogrifier.reindexobject
    ...
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.reindexobject', reindexobject)

    >>> transmogrifier(u'plone.app.transmogrifier.tests.reindexobject') 
    >>> print(handler)
    logger INFO
      {'_path': '/spam/eggs/foo'}
    logger INFO
      {'_path': '/spam/eggs/bar'}
    logger INFO
      {'_path': '/spam/eggs/baz'}
    logger INFO
        {'_path': 'not/a/catalog/aware/content',
       'title': 'Should not be reindexed, not a CMFCatalogAware content'}
    logger INFO
        {'_path': 'not/existing/bar',
       'title': 'Should not be reindexed, not an existing path'}

    >>> pprint.pprint(plone.reindexed)
    [('spam/eggs/foo', 'reindexed'),
     ('spam/eggs/bar', 'reindexed'),
     ('spam/eggs/baz', 'reindexed')]
