URL Normalizer section
----------------------

A URLNormalizer section allows you to parse any piece of text into a url-safe
string which is then assigned to a specified key. It uses plone.i18n.normalizer
to perform the normalization. The url normalizer section blueprint name is
``plone.app.transmogrifier.urlnormalizer``.

The URL normalizer accepts the following optional keys -
``source-key``: The name of the object key that you wish to normalize,
``destination-key``: Where you want the normalized string to be stored,
``locale``: if you want the normalizer to be aware of locale, use this.

::

    >>> import pprint
    >>> urlnormalizer = """
    ... [transmogrifier]
    ... pipeline =
    ...     urlnormalizersource
    ...     urlnormalizer
    ...     printer
    ...     
    ... [urlnormalizersource]
    ... blueprint = plone.app.transmogrifier.tests.urlnormalizersource
    ... 
    ... [urlnormalizer]
    ... blueprint = plone.app.transmogrifier.urlnormalizer
    ... source-key = title
    ... destination-key = string:id
    ... locale = string:en
    ... 
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.urlnormalizer',
    ...                urlnormalizer)
    >>> transmogrifier(u'plone.app.transmogrifier.tests.urlnormalizer')
    >>> print(handler)
    logger INFO
      {'id': 'mytitle', 'title': 'mytitle'}
    logger INFO
      {'id': 'is-this-a-title-of-any-sort', 'title': 'Is this a title of any sort?'}
    logger INFO
        {'id': 'put-some-br-1lly-v4lues-here-there',
       'title': 'Put some <br /> $1llY V4LUES -- here&there'}
    logger INFO
        {'id': 'what-about-line-breaks-system',
       'title': 'What about \r\n line breaks (system)'}
    logger INFO
      {'id': 'try-one-of-these-oh', 'title': 'Try one of these --------- oh'}
    logger INFO
      {'language': 'My language is de'}
    logger INFO
      {'language': 'my language is en'}

As you can see, only items containing the specified source-key have been
processed, the others have been ignored and yielded without change.

Destination-key and locale accept TALES expressions, so for example you could
set your destination-key based on your locale element, which is in turn derived
from your source-key:

::

    >>> import pprint
    >>> urlnormalizer = """
    ... [transmogrifier]
    ... pipeline =
    ...     urlnormalizersource
    ...     urlnormalizer
    ...     printer
    ...     
    ... [urlnormalizersource]
    ... blueprint = plone.app.transmogrifier.tests.urlnormalizersource
    ... 
    ... [urlnormalizer]
    ... blueprint = plone.app.transmogrifier.urlnormalizer
    ... source-key = language
    ... locale = python:str(item.get('${urlnormalizer:source-key}', 'na')[-2:])
    ... destination-key = ${urlnormalizer:locale}
    ... 
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.urlnormalizer2',
    ...                urlnormalizer)

    >>> handler.clear()
    >>> transmogrifier(u'plone.app.transmogrifier.tests.urlnormalizer2')
    >>> print(handler)
    logger INFO
      {'title': 'mytitle'}
    logger INFO
      {'title': 'Is this a title of any sort?'}
    logger INFO
      {'title': 'Put some <br /> $1llY V4LUES -- here&there'}
    logger INFO
      {'title': 'What about \r\n line breaks (system)'}
    logger INFO
      {'title': 'Try one of these --------- oh'}
    logger INFO
      {'de': 'my-language-is-de', 'language': 'My language is de'}
    logger INFO
      {'en': 'my-language-is-en', 'language': 'my language is en'}

In this case only items containing the 'language' key have been processed, and
the destination-key has been set to the same value as the locale was. This is
more to illuminate the fact that the locale was set, rather than providing a
sensible use-case for destination-key.

If ZERO options are specified, the normalizer falls back to a set of default
values as follows:
``source-key``: title,
``locale``: en,
``destination-key``: _id

::

    >>> import pprint
    >>> urlnormalizer = """
    ... [transmogrifier]
    ... pipeline =
    ...     urlnormalizersource
    ...     urlnormalizer
    ...     printer
    ...     
    ... [urlnormalizersource]
    ... blueprint = plone.app.transmogrifier.tests.urlnormalizersource
    ... 
    ... [urlnormalizer]
    ... blueprint = plone.app.transmogrifier.urlnormalizer
    ... 
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.urlnormalizer3',
    ...                urlnormalizer)

    >>> handler.clear()
    >>> transmogrifier(u'plone.app.transmogrifier.tests.urlnormalizer3')
    >>> print(handler)
    logger INFO
      {'_id': 'mytitle', 'title': 'mytitle'}
    logger INFO
      {'_id': 'is-this-a-title-of-any-sort', 'title': 'Is this a title of any sort?'}
    logger INFO
        {'_id': 'put-some-br-1lly-v4lues-here-there',
       'title': 'Put some <br /> $1llY V4LUES -- here&there'}
    logger INFO
        {'_id': 'what-about-line-breaks-system',
       'title': 'What about \r\n line breaks (system)'}
    logger INFO
      {'_id': 'try-one-of-these-oh', 'title': 'Try one of these --------- oh'}
    logger INFO
      {'language': 'My language is de'}
    logger INFO
      {'language': 'my language is en'}

In this case, the destination-key is set to a controller variable, like _path,
as it is expected that the newly formed Id will in most cases be used further
down the pipeline in constructing the full, final path to the new Plone object.

It should be noted that this section can effectively transform *any* section of
text and turn it into a normalized, web safe string (max 255 chars) This string
does not necessarily need to be used for a URL.
