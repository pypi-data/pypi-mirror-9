from DateTime import DateTime
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import traverse
from zope.interface import classProvides
from zope.interface import implements


class DatesUpdater(object):
    """Sets creation and modification dates on objects.
    """
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        """
        :param options['path-key']: The key, under the path can be found in
                                    the item.
        :param options['creation-key']: Creation date key. Defaults to
                                        creation_date.
        :param options['modification-key']: Modification date key. Defaults to
                                            modification_date.
        """
        self.previous = previous
        self.context = transmogrifier.context

        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.creationkey = options.get('creation-key', 'creation_date')
        self.modificationkey = options.get('modification-key', 'modification_date')  # noqa

    def __iter__(self):

        for item in self.previous:

            pathkey = self.pathkey(*item.keys())[0]
            if not pathkey:  # not enough info
                yield item
                continue
            path = item[pathkey]

            ob = traverse(self.context, str(path).lstrip('/'), None)
            if ob is None:
                yield item
                continue  # object not found

            creationdate = item.get(self.creationkey, None)
            if creationdate and getattr(ob, 'creation_date', False):
                ob.creation_date = DateTime(creationdate)

            modificationdate = item.get(self.modificationkey, None)
            if modificationdate and getattr(ob, 'modification_date', False):
                ob.modification_date = DateTime(modificationdate)

            yield item
