Portal Transforms section
-------------------------

A portal transforms pipeline section lets you use Portal Transforms to
transform item values. The portal transforms section blueprint name is
``plone.app.transmogrifier.portaltransforms``.

What values to transform is determined by the ``keys`` option, which takes a
set of newline-separated key names. If a key name starts with ``re:`` or
``regexp:`` it is treated as a regular expression instead.

You can specify what transformation to apply in two ways. Firstly, you can
directly specify a transformation by naming it with the ``transform`` option;
the named transformation is run directly. Alternatively you can let the portal
transforms tool figure out what transform to use by specifying ``target`` and
an optional ``from`` mimetype. The portal transforms tool will select one or
more transforms based on these mimetypes, and if no ``from`` option is given
the original item value is used to determine one.

Also optional is the ``condition`` option, which lets you specify a TALES
expression that when evaluating to False will prevent any transformations from
happening. The condition is evaluated for every matched key.

::

    >>> ptransforms = """
    ... [transmogrifier]
    ... pipeline =
    ...     source
    ...     transform-id
    ...     transform-title
    ...     transform-status
    ...     printer
    ... 
    ... [source]
    ... blueprint = collective.transmogrifier.sections.tests.samplesource
    ... encoding = utf8
    ... 
    ... [transform-id]
    ... blueprint = plone.app.transmogrifier.portaltransforms
    ... transform = identity
    ... keys = id
    ...
    ... [transform-title]
    ... blueprint = plone.app.transmogrifier.portaltransforms
    ... target = text/plain
    ... keys = title
    ... 
    ... [transform-status]
    ... blueprint = plone.app.transmogrifier.portaltransforms
    ... from = text/plain
    ... target = text/plain
    ... keys = status
    ... 
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.ptransforms',
    ...                ptransforms)

    >>> transmogrifier(u'plone.app.transmogrifier.tests.ptransforms')
    >>> print handler
    logger INFO
        {'id': "Transformed 'foo' using the identity transform",
       'status': "Transformed '\\xe2\\x84\\x97' from text/plain to text/plain",
       'title': "Transformed 'The Foo Fighters \\xe2\\x84\\x97' to text/plain"}
    logger INFO
        {'id': "Transformed 'bar' using the identity transform",
       'status': "Transformed '\\xe2\\x84\\xa2' from text/plain to text/plain",
       'title': "Transformed 'Brand Chocolate Bar \\xe2\\x84\\xa2' to text/plain"}
    logger INFO
        {'id': "Transformed 'monty-python' using the identity transform",
       'status': "Transformed '\\xc2\\xa9' from text/plain to text/plain",
       'title': 'Transformed "Monty Python\'s Flying Circus \\xc2\\xa9" to text/plain'}

The ``condition`` expression has access to the following:

``item``
    The current pipeline item

``key``
    The name of the matched key

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
