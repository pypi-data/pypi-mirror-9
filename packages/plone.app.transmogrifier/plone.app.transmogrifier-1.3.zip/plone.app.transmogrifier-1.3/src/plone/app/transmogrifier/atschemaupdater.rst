ATSchema updater section
------------------------

An AT schema updater pipeline section is another important transmogrifier
content import pipeline element. It updates field values for Archetypes
objects based on their schema based on the items it processes. The AT schema
updater section blueprint name is
``plone.app.transmogrifier.atschemaupdater``. AT Schema updater sections
operate on objects already present in the ZODB, be they created by a
constructor or pre-existing objects.

Schema updating needs at least 1 piece of information: the path to the object
to update. To determine the path, the schema updater section inspects each
item and looks for one key, as described below. Any item missing this piece of
information will be skipped. Similarly, items with a path that doesn't exist
or are not Archetypes objects will be skipped as well.

For the object path, it'll look (in order) for
``_plone.app.transmogrifier.atschemaupdater_[sectionname]_path``,
``_plone.app.transmogrifier.atschemaupdater_path``, ``_[sectionname]_path``
and ``_path``, where ``[sectionname]`` is replaced with the name given to the
current section. This allows you to target the right section precisely if
needed. Alternatively, you can specify what key to use for the path by
specifying the ``path-key`` option, which should be a list of keys to try (one
key per line, use a ``re:`` or ``regexp:`` prefix to specify regular
expressions).

Paths to objects are always interpreted as relative to the context. Any
writable field who's id matches a key in the current item will be updated with
the corresponding value, using the field's mutator.

::

    >>> import pprint
    >>> atschema = """
    ... [transmogrifier]
    ... pipeline =
    ...     schemasource
    ...     schemaupdater
    ...     printer
    ...     
    ... [schemasource]
    ... blueprint = plone.app.transmogrifier.tests.schemasource
    ... 
    ... [schemaupdater]
    ... blueprint = plone.app.transmogrifier.atschemaupdater
    ... 
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.atschema', atschema)

    >>> transmogrifier(u'plone.app.transmogrifier.tests.atschema')
    >>> print handler
    logger INFO
        {'_path': '/spam/eggs/foo',
       'fieldnotchanged': 'nochange',
       'fieldone': 'one value',
       'fieldtwo': 2,
       'fieldunicode': u'\xe5',
       'nosuchfield': 'ignored'}
    logger INFO
        {'_path': 'not/existing/bar',
       'fieldone': 'one value',
       'title': 'Should not be updated, not an existing path'}
    logger INFO
      {'fieldone': 'one value', 'title': 'Should not be updated, no path'}
    logger INFO
        {'_path': '/spam/eggs/notatcontent',
       'fieldtwo': 2,
       'title': 'Should not be updated, not an AT base object'}
    >>> pprint.pprint(plone.updated)
    [('spam/eggs/foo', 'fieldone', 'one value-by-mutator'),
     ('spam/eggs/foo', 'fieldtwo', 2)]
