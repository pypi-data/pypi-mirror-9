PathFixer section
-----------------

When importing contents from a old site into a new, the path to the Plone site
root may have changed. This blueprint updates the old paths to match the new
structrue by removing or appending strings from the right side of the path
value.

Blueprint name: ``plone.app.transmogrifier.pathfixer``

Option path-key: The key of the item under which the path to be manipulated can
                 be found. E.g. ``_path``. 

Option stripstring: A string to strip from the path value.

Option prependstring: A string to append to the path value.


Look, here. Original path structure from
plone.app.transmogrifier.tests.schemasource is::

    /spam/eggs/foo
    relative/path
    /spam/eggs/another


Now lets manipulate it::

    >>> import pprint
    >>> pipeline = """
    ... [transmogrifier]
    ... pipeline =
    ...     schemasource
    ...     pathfixer
    ...     logger
    ...     
    ... [schemasource]
    ... blueprint = plone.app.transmogrifier.tests.schemasource
    ... 
    ... [pathfixer]
    ... blueprint = plone.app.transmogrifier.pathfixer
    ... path-key = _path
    ... stripstring = /spam/eggs/
    ... prependstring = subfolder/
    ... 
    ... [logger]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... key = _path
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.pathfixer', pipeline)

    >>> transmogrifier(u'plone.app.transmogrifier.tests.pathfixer')
    >>> print handler
    logger INFO
      subfolder/foo
    logger INFO
      subfolder/relative/path
    logger INFO
      subfolder/another

