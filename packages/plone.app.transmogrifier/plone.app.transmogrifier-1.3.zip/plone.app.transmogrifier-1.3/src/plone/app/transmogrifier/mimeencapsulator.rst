Mime encapsulator section
-------------------------

A mime encapsulator section wraps arbitrary data in ``OFS.Image.File``
objects, together with a MIME type. This wrapping is a pre-requisite for
Archetypes image, file or text fields, which can only take such File objects.
The mime encapsulator blueprint name is
``plone.app.transmogrifier.mimeencapsulator``. 

An encapsulator section needs 3 pieces of information: the key at which to
find the data to encapsulate, the MIME type of this data, and the name of the
field where the encapsulated data will be stored. The idea is that the data
is copied from a "data key" (defaulting to ``_data`` and settable with the
``data-key`` option), wrapped into a ``File`` object with a MIME type (read
from the ``mimetype`` option, which contains a TALES expression), and then
saved into the pipeline item dictionary under a new key, most likely
corresponding to an Archetypes field name (read from the ``field`` option,
which is also a TALES expression).

The data key defaults to the series ``_[blueprintname]_[sectionname]_data``,
``_[blueprintname]_data``, ``_[sectionname]_data`` and ``_data``, where 
``[blueprintname]`` is ``plone.app.transmogrifier.mimeencapsulator`` and
``[sectionname]`` is replaced with the name of the current section. You can
override this by specifying the ``data-key`` option.

You specify the mimetype with the ``mimetype`` option, which takes a TALES 
expression.

The ``field`` option, also a TALES expression, sets the output field name.

Optionally, you can specify a ``condition`` option, again a TALES expression,
that when evaluating to ``False``, causes the section to skip encapsulation
for  that item.

::

    >>> encapsulator = """
    ... [transmogrifier]
    ... pipeline =
    ...     source
    ...     encapsulator
    ...     conditionalencapsulator
    ...     printer
    ...
    ... [source]
    ... blueprint = plone.app.transmogrifier.tests.encapsulatorsource
    ...
    ... [encapsulator]
    ... blueprint = plone.app.transmogrifier.mimeencapsulator
    ... # Read the mimetype from the item
    ... mimetype = item/_mimetype
    ... field = string:datafield
    ...
    ... [conditionalencapsulator]
    ... blueprint = plone.app.transmogrifier.mimeencapsulator
    ... data-key = portrait
    ... mimetype = python:item.get('_%s_mimetype' % key)
    ... # replace the data in-place
    ... field = key
    ... condition = mimetype
    ... 
    ... [printer]
    ... blueprint = plone.app.transmogrifier.tests.ofsfileprinter
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.encapsulator',
    ...                encapsulator)
    >>> transmogrifier(u'plone.app.transmogrifier.tests.encapsulator')
    datafield: (application/x-test-data) foobarbaz
    portrait: (image/jpeg) someportraitdata


The ``field`` expression has access to the following:

``item``
    The current pipeline item

``key``
    The name of the matched data key

``match``
    If the key was matched by a regular expression, the match object, otherwise boolean True

``transmogrifier``
    The transmogrifier

``name``
    The name of the splitter section

``options``
    The splitter options

``modules``
    ``sys.modules``


The ``mimetype`` expression has access to the same information as the ``field``
expression, plus:

``field``
    The name of the field in which the encapsulated data will be stored.

The ``condition`` expression has access to the same information as the
``mimetype`` expression, plus:

``mimetype``
    The mimetype used to encapsulate the data.
