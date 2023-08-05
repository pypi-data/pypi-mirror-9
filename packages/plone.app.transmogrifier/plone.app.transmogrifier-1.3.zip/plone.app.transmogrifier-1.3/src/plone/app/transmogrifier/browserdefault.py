from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault
from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import traverse
from zope.interface import classProvides, implements


class BrowserDefaultSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context

        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.layoutkey = defaultMatcher(options, 'layout-key', name, 'layout')
        self.defaultpagekey = defaultMatcher(options, 'default-page-key', name,
                                             'defaultpage')

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            if not pathkey:
                yield item
                continue

            layoutkey = self.layoutkey(*item.keys())[0]
            defaultpagekey = self.defaultpagekey(*item.keys())[0]

            path = item[pathkey]

            obj = traverse(self.context, str(path).lstrip('/'), None)
            if obj is None:
                yield item
                continue

            if not ISelectableBrowserDefault.providedBy(obj):
                yield item
                continue

            if layoutkey:
                layout = item[layoutkey]
                if layout:
                    obj.setLayout(layout)

            if defaultpagekey:
                defaultpage = item[defaultpagekey]
                if defaultpage:
                    obj.setDefaultPage(defaultpage)

            yield item
