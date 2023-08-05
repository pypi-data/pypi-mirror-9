Criterion adder section
-----------------------

A criterion adder section is used to add criteria to collections. It's section
blueprint name is ``plone.app.transmogrifier.criterionadder``. Criterion adder
sections operate on objects already present in the ZODB, be they created by a
constructor or pre-existing objects.

Given a path, a criterion type and a field name, this section will look up
a Collection at the given path, and add a criterion field, then alter the
path of the item so further sections will act on the added criterion. For
example, an item with keys ``_path=bar/baz``, ``_field=modified`` and
``_criterion=ATFriendlyDateCriteria`` will result in a new date criterion
added inside the bar/baz collection, and the item's path will be updated
to ``bar/baz/crit__ATFriendlyDateCriteria_modified``.

For the  path, criterion type and field keys, it'll look (in order) for
``_plone.app.transmogrifier.atschemaupdater_[sectionname]_[key]``,
``_plone.app.transmogrifier.atschemaupdater_[key]``, ``_[sectionname]_[key]``
and ``_[key]``, where ``[sectionname]`` is replaced with the name given to the
current section and ``[key]`` is ``path``, ``criterion`` and ``field``
respectively. This allows you to target the right section precisely if
needed. Alternatively, you can specify what key to use for these by
specifying the ``path-key``, ``criterion-key`` and ``field-key`` options, 
which should be a list of keys to try (one key per line, use a ``re:`` or
``regexp:`` prefix to specify regular expressions).

Paths to objects are always interpreted as relative to the context, and must
resolve to IATTopic classes.

::

    >>> import pprint
    >>> criteria = """
    ... [transmogrifier]
    ... pipeline =
    ...     criteriasource
    ...     criterionadder
    ...     printer
    ...     
    ... [criteriasource]
    ... blueprint = plone.app.transmogrifier.tests.criteriasource
    ... 
    ... [criterionadder]
    ... blueprint = plone.app.transmogrifier.criterionadder
    ... 
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.criteria', criteria)
    >>> transmogrifier(u'plone.app.transmogrifier.tests.criteria')
    >>> print(handler)
    logger INFO
      {'_criterion': 'bar', '_field': 'baz', '_path': '/spam/eggs/foo/crit__baz_bar'}
    logger INFO
        {'_criterion': 'bar',
       '_field': 'baz',
       '_path': 'not/existing/bar',
       'title': 'Should not be updated, not an existing path'}
    logger INFO
        {'_path': 'spam/eggs/incomplete',
       'title': 'Should not be updated, no criterion or field'}
    >>> pprint.pprint(plone.criteria)
    [('spam/eggs/foo', 'baz', 'bar')]
