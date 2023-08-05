UID updater section
-------------------

If an Archetypes content object is created in a pipeline, e.g. by the standard
content constructor section, it will get a new UID. If you are importing
content from another Plone site, and you have references (or links embedded
in content using Plone's link-by-UID feature) to existing content, you may
want to retain UIDs. The UID updater section allows you to set the UID on an
existing object for this purpose.

The UID updater blueprint name is ``plone.app.transmogrifier.uidupdater``.

UID updating requires two pieces of information: the path to the object
to update, and the new UID to set.

To determine the path, the UID updater section inspects each item and looks
for a path key, as described below. Any item missing this key will be skipped.
Similarly, items with a path that doesn't exist or are not referenceable 
(Archetypes) objects will be skipped.

The object path will be found under the first key found among the following:

* ``_plone.app.transmogrifier.atschemaupdater_[sectionname]_path``
* ``_plone.app.transmogrifier.atschemaupdater_path``
* ``_[sectionname]_path``
* ``_path``

where ``[sectionname]`` is replaced with the name given to the current
section. This allows you to target the right section precisely if
needed.

Alternatively, you can specify what key to use for the path by specifying the
``path-key`` option, which should be a list of keys to try (one key per line;
use a ``re:`` or ``regexp:`` prefix to specify regular expressions).

Paths to objects are always interpreted as relative to the context.

Similarly, the UID to set must be a string under a given key. You can set the
key with the ``uid-key`` option, which behaves much like ``path-key``. The
default is to look under:

* ``_plone.app.transmogrifier.atschemaupdater_[sectionname]_uid``
* ``_plone.app.transmogrifier.atschemaupdater_uid``
* ``_[sectionname]_uid``
* ``_uid``

If the UID key is missing, the item will be skipped.

Below is an example of a standard updater. The test uid source produces
items with two keys: a path under ``_path`` and a UID string under ``_uid``.

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
    ... blueprint = plone.app.transmogrifier.tests.uidsource
    ... 
    ... [schemaupdater]
    ... blueprint = plone.app.transmogrifier.uidupdater
    ... 
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.uid', atschema)
    >>> transmogrifier(u'plone.app.transmogrifier.tests.uid')
    >>> print(handler)
    logger INFO
      {'_path': '/spam/eggs/foo', '_uid': 'abc'}
    logger INFO
      {'_path': '/spam/eggs/bar', '_uid': 'xyz'}
    logger INFO
      {'_path': 'not/existing/bar', '_uid': 'def'}
    logger INFO
      {'_uid': 'geh'}
    logger INFO
      {'_path': '/spam/eggs/baz'}
    logger INFO
      {'_path': '/spam/notatcontent', '_uid': 'ijk'}
    
    >>> pprint.pprint(plone.uids_set)
    [('spam/eggs/foo', 'abc')]
