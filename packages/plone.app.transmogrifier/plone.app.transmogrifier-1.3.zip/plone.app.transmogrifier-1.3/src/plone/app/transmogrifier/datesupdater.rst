PathFixer section
-----------------

When importing contents from a old site into a new, the path to the Plone site
root may have changed. This blueprint updates the old paths to match the new
structrue by removing or appending strings from the right side of the path
value.

Blueprint name: ``plone.app.transmogrifier.pathfixer``

Option path-key: The key for the path to the object.

Option creation-key: The key for the creation date.

Option modification-key: The key for the modification date.

::

    >>> import pprint
    >>> pipeline = """
    ... [transmogrifier]
    ... pipeline =
    ...     schemasource
    ...     datesupdater
    ...     logger
    ...     
    ... [schemasource]
    ... blueprint = plone.app.transmogrifier.tests.schemasource
    ... 
    ... [datesupdater]
    ... blueprint = plone.app.transmogrifier.datesupdater
    ... path-key = _path
    ... creation-key = creation_date
    ... modification-key = modification_date
    ... 
    ... [logger]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.datesupdater', pipeline)

    >>> transmogrifier(u'plone.app.transmogrifier.tests.datesupdater')


Print out the source structure::

    >>> print handler
    logger INFO
        {'_path': '/spam/eggs/foo',
       'creation_date': DateTime('2010/10/10 00:00:00 GMT+2'),
       'modification_date': DateTime('2012/12/12 00:00:00 GMT+1')}
    logger INFO
        {'_path': '/spam/eggs/bar',
       'creation_date': DateTime('2010/10/10 00:00:00 GMT+2')}
    logger INFO
        {'_path': '/spam/eggs/baz',
       'modification_date': DateTime('2012/12/12 00:00:00 GMT+1')}
    logger INFO
        {'_path': 'not/existing/bar',
       'creation_date': DateTime('2010/10/10 00:00:00 GMT+2'),
       'modification_date': DateTime('2012/12/12 00:00:00 GMT+1')}
    logger INFO
        {'creation_date': DateTime('2010/10/10 00:00:00 GMT+2'),
       'modification_date': DateTime('2012/12/12 00:00:00 GMT+1')}


That was changed on the object::

    >>> pprint.pprint(plone.updated)
    [('spam/eggs/foo', 'creation_date', DateTime('2010/10/10 00:00:00 GMT+2')),
     ('spam/eggs/foo', 'modification_date', DateTime('2012/12/12 00:00:00 GMT+1')),
     ('spam/eggs/bar', 'creation_date', DateTime('2010/10/10 00:00:00 GMT+2')),
     ('spam/eggs/baz', 'modification_date', DateTime('2012/12/12 00:00:00 GMT+1'))]

