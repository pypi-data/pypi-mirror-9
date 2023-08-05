from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Condition
from collective.transmogrifier.utils import defaultKeys, defaultMatcher
from collective.transmogrifier.utils import pathsplit
from collective.transmogrifier.utils import traverse
from plone.app.redirector.interfaces import IRedirectionStorage
from zope.component import queryUtility
from zope.interface import classProvides, implements
import logging
import posixpath
import urlparse


from xml.etree.ElementTree import Element
try:
    from lxml.etree import ElementBase
except ImportError:
    ElementBase = Element


class RedirectorSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.condition = Condition(options.get('condition', 'python:True'),
                                   transmogrifier, name, options)

        self.context = transmogrifier.context
        self.context_path = '/'.join(self.context.getPhysicalPath()) + '/'
        self.context_url = self.context.absolute_url()
        self.logger = logging.getLogger(name)

        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.oldpathskey = defaultMatcher(
            options, 'old-paths-key', name, 'old_paths')

        self.updatepathkeys = defaultMatcher(
            options, 'update-path-keys', name, 'update_path',
            extra=(('_content_element', 'remoteUrl', 'relatedItems') +
                   defaultKeys(options['blueprint'], name, 'path')))

        self.elementattribs = options.get('element-attributes',
                                          ('href', 'src'))

    def __iter__(self):
        storage = queryUtility(IRedirectionStorage)
        for item in self.previous:
            if storage is None:
                self.logger.warn(
                    'Could not find plone.app.redirector storage utility')
                yield item
                continue

            keys = item.keys()

            # Update paths first

            # If a redirect already exists for _path, it should be
            # updated first so that any new redirects for _old_paths
            # point to the correct _path and it's unlikely that any
            # keys in this item will contain any _old_paths for the
            # same item

            for key in keys:
                if not self.updatepathkeys(key)[1]:
                    continue

                if not self.condition(item, key=key):
                    continue

                multiple = True
                paths = old_paths = item[key]
                if not isinstance(paths, (tuple, list)):
                    multiple = False
                    paths = [paths]

                for idx, obj in enumerate(paths):
                    path = obj
                    is_element = isinstance(obj, (Element, ElementBase))
                    if is_element:
                        for attrib in self.elementattribs:
                            if attrib in obj.attrib:
                                path = obj.attrib[attrib]
                                break
                        else:
                            # No attribute in this element
                            continue

                    leading = path[:-len(path.lstrip('/'))]
                    url = urlparse.urlsplit(path)
                    if self._is_external(url):
                        continue

                    abspath = posixpath.abspath(posixpath.join(
                        posixpath.sep, str(url.path).lstrip('/'))).lstrip('/')
                    new_path = old_path = self.context_path
                    for elem in pathsplit(abspath):
                        old_path = posixpath.join(old_path, elem)
                        new_path = posixpath.join(new_path, elem)
                        new_path = storage.get(old_path, new_path)
                    if not urlparse.urlsplit(new_path).netloc:
                        new_path = leading + new_path[len(self.context_path):]
                    new_path = urlparse.urlunsplit(
                        url[:2] + (new_path, ) + url[3:])

                    if new_path != path.lstrip('/'):
                        if is_element:
                            obj.attrib[attrib] = new_path
                            new_path = obj
                        paths[idx] = new_path

                if not multiple:
                    paths = paths[0]
                if item[key] != paths:
                    self.logger.debug('Updating %r path(s): %r => %r',
                                      key, old_paths, paths)
                    item[key] = paths

            # Collect old paths
            old_paths = set()
            oldpathskey = self.oldpathskey(*keys)[0]
            if oldpathskey and oldpathskey in item:
                paths = item[oldpathskey]
                if isinstance(paths, (str, unicode)):
                    paths = [paths]
                old_paths.update(paths)

            pathkey = self.pathkey(*keys)[0]
            if pathkey:
                path = item[pathkey]
                url = urlparse.urlsplit(path)
                new_path = (
                    self._is_external(url) and path
                    or posixpath.join(self.context_path,
                                      str(path).lstrip('/'))).rstrip('/')
                # Add any new redirects
                for old_path in old_paths:
                    old_path = posixpath.join(
                        self.context_path,
                        str(old_path).lstrip('/')).rstrip('/')
                    if (old_path and old_path != new_path
                            # Avoid recursive redirects
                            and not new_path.startswith(old_path + '/')
                            and not storage.has_path(old_path)
                            and traverse(self.context, old_path) is None):
                        self.logger.debug('Adding %r redirect: %r => %r',
                                          pathkey, old_path, new_path)
                        storage.add(old_path, new_path)

            yield item

    def _is_external(self, url):
        return url.netloc and not url.geturl().startswith(self.context_url)
