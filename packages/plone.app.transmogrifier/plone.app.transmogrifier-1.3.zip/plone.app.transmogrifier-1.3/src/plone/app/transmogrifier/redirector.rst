Redirector section
------------------

A redirector section uses `plone.app.redirector` to manage redirects and update
paths in keys.

::

    >>> import pprint
    >>> redirector = """
    ... [transmogrifier]
    ... pipeline =
    ...     source
    ...     clean-old-paths
    ...     old-paths
    ...     content-element
    ...     redirect
    ...     href
    ...     logger
    ... 
    ... [source]
    ... blueprint = collective.transmogrifier.sections.csvsource
    ... filename = plone.app.transmogrifier:redirector.csv
    ... 
    ... [clean-old-paths]
    ... blueprint = collective.transmogrifier.sections.manipulator
    ... condition = not:item/_old_paths|nothing
    ... delete = _old_paths
    ... 
    ... [old-paths]
    ... blueprint = collective.transmogrifier.sections.inserter
    ... key = string:_old_paths
    ... condition = exists:item/_old_paths
    ... value = python:item['_old_paths'].split('|')
    ... 
    ... [content-element]
    ... blueprint = collective.transmogrifier.sections.inserter
    ... key = string:_content_element
    ... condition = item/remoteUrl
    ... value = python:modules['xml.etree.ElementTree'].Element(\
    ...     'a', dict(href=item['remoteUrl']))
    ... 
    ... [redirect]
    ... blueprint = plone.app.transmogrifier.redirector
    ... 
    ... [href]
    ... blueprint = collective.transmogrifier.sections.inserter
    ... key = string:_content_element
    ... condition = exists:item/_content_element
    ... value = python:item['_content_element'].attrib['href']
    ... 
    ... [logger]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... level = INFO
    ... """
    >>> registerConfig(
    ...     u'plone.app.transmogrifier.tests.redirector', redirector)

    >>> transmogrifier(u'plone.app.transmogrifier.tests.redirector')
    >>> print handler
    logger INFO
      {'_old_paths': ['corge', 'waldo'], '_redirect_path': 'foo', 'remoteUrl': ''}
    logger INFO
      {'_redirect_path': 'foo', 'remoteUrl': ''}
    logger INFO
        {'_old_paths': ['corge/item-00', 'waldo/item-00'],
       '_redirect_path': 'foo/item-00',
       'remoteUrl': ''}
    logger INFO
        {'_content_element': 'foo/item-00',
       '_old_paths': ['corge/grault', 'waldo/fred'],
       '_redirect_path': 'foo/bar',
       'remoteUrl': 'foo/item-00'}
    logger INFO
        {'_content_element': '/foo/item-00#fragment',
       '_old_paths': ['corge/grault/item-01', 'waldo/fred/item-01'],
       '_redirect_path': 'http://nohost/foo/bar/item-01',
       'remoteUrl': '/foo/item-00#fragment'}
    logger INFO
      {'_redirect_path': '/foo/bar/qux', 'remoteUrl': ''}
    logger INFO
        {'_content_element': 'http://nohost/foo/bar/item-01',
       '_redirect_path': '/foo/bar/qux/item-02',
       'remoteUrl': 'http://nohost/foo/bar/item-01'}

    >>> import pprint
    >>> from zope.component import getUtility
    >>> from plone.app.redirector.interfaces import IRedirectionStorage
    >>> storage = getUtility(IRedirectionStorage)
    >>> pprint.pprint(dict((path, storage.get(path)) for path in storage))
    {'/plone/corge': '/plone/foo',
     '/plone/corge/grault': '/plone/foo/bar',
     '/plone/corge/grault/item-01': 'http://nohost/foo/bar/item-01',
     '/plone/corge/item-00': '/plone/foo/item-00',
     '/plone/waldo': '/plone/foo',
     '/plone/waldo/fred': '/plone/foo/bar',
     '/plone/waldo/fred/item-01': 'http://nohost/foo/bar/item-01',
     '/plone/waldo/item-00': '/plone/foo/item-00'}
