from DateTime.DateTime import DateTime
from Products.Five import zcml
from collective.transmogrifier.interfaces import ISectionBlueprint, ISection
from collective.transmogrifier.sections.tests import MockObjectManager
from collective.transmogrifier.sections.tests import SampleSource
from collective.transmogrifier.sections.tests import _marker
from collective.transmogrifier.sections.tests import sectionsSetUp as ctSectionsSetup  # noqa
from collective.transmogrifier.tests import tearDown
from zope.component import provideUtility
from zope.interface import classProvides, implements
from zope.testing import doctest
import posixpath
import unittest

# Doctest support

optionflags = doctest.REPORT_NDIFF


def sectionsSetUp(test):
    ctSectionsSetup(test)
    import plone.app.transmogrifier
    zcml.load_config('configure.zcml', plone.app.transmogrifier)


class MockObjectManager(MockObjectManager):

    def _getOb(self, id_, default=_marker):
        obj = super(MockObjectManager, self)._getOb(id_, default=default)
        if getattr(obj, '_path', '').endswith('/notatcontent'):
            return object()
        return obj


def portalTransformsSetUp(test):
    sectionsSetUp(test)

    class MockPortalTransforms(object):

        def __call__(self, transform, data):
            return 'Transformed %r using the %s transform' % (data, transform)

        def convertToData(self, target, data, mimetype=None):
            if mimetype is not None:
                return 'Transformed %r from %s to %s' % (
                    data, mimetype, target)
            else:
                return 'Transformed %r to %s' % (data, target)
    test.globs['plone'].portal_transforms = MockPortalTransforms()


def aTSchemaUpdaterSetUp(test):
    sectionsSetUp(test)

    from Products.Archetypes.interfaces import IBaseObject

    class MockPortal(MockObjectManager):
        implements(IBaseObject)

        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == '/':
                return False  # path is absolute
            if isinstance(path, unicode):
                return False
            if path == 'not/existing/bar':
                return False
            return True

        _last_field = []

        def getField(self, name):
            if name.startswith('field'):
                self._last_field[:] = [name]
                return self

        def get(self, ob):
            if self._last_field[0].endswith('notchanged'):
                return 'nochange'
            if self._last_field[0].endswith('unicode'):
                return u'\xe5'.encode('utf8')

        @property
        def accessor(self):
            if self._last_field[0] == 'fieldone':
                return 'accessor_method'
            else:
                return None

        def accessor_method(self):
            return '%s-by-mutator' % self.get(self)

        updated = []

        def set(self, ob, val):
            self.updated.append((self._last_path[0], self._last_field[0], val))

        @property
        def mutator(self):
            if self._last_field[0] == 'fieldone':
                return 'mutator_method'
            else:
                return None

        def mutator_method(self, value):
            return self.set(self, '%s-by-mutator' % value)

        def checkCreationFlag(self):
            return len(self.updated) % 2

        def unmarkCreationFlag(self):
            pass

        def at_post_create_script(self):
            pass

        def at_post_edit_script(self):
            pass

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class SchemaSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(SchemaSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo', fieldone='one value',
                     fieldtwo=2, nosuchfield='ignored',
                     fieldnotchanged='nochange', fieldunicode=u'\xe5',),
                dict(_path='not/existing/bar', fieldone='one value',
                     title='Should not be updated, not an existing path'),
                dict(fieldone='one value',
                     title='Should not be updated, no path'),
                dict(_path='/spam/eggs/notatcontent', fieldtwo=2,
                     title='Should not be updated, not an AT base object'),
            )
    provideUtility(SchemaSource,
                   name=u'plone.app.transmogrifier.tests.schemasource')


def workflowUpdaterSetUp(test):
    sectionsSetUp(test)

    from Products.CMFCore.WorkflowCore import WorkflowException

    class MockPortal(MockObjectManager):

        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == '/':
                return False  # path is absolute
            if isinstance(path, unicode):
                return False
            if path == 'not/existing/bar':
                return False
            return True

        @property
        def portal_workflow(self):
            return self

        updated = []

        workflow_history = {}

        def doActionFor(self, ob, action):
            assert isinstance(ob, self.__class__)
            if action == 'nonsuch':
                raise WorkflowException('Test exception')
            self.updated.append((self._last_path[0], action))

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class WorkflowSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(WorkflowSource, self).__init__(*args, **kw)
            self.sample = (
                dict(
                    _path='/spam/eggs/foo',
                    _transitions='spam'),
                dict(
                    _path='/spam/eggs/baz',
                    _transitions=(
                        'spam',
                        'eggs')),
                dict(
                    _path='not/existing/bar',
                    _transitions=(
                        'spam',
                        'eggs'),
                    title='Should not be updated, not an existing path'),
                dict(
                    _path='spam/eggs/incomplete',
                    title='Should not be updated, no transitions'),
                dict(
                    _path='/spam/eggs/nosuchtransition',
                    _transitions=(
                        'nonsuch',
                    ),
                    title='Should not be updated, no such transition'),
                dict(
                    _path='/spam/eggs/bla',
                    _transitions=(
                        {
                            'action': 'spam',
                            'review_state': 'spammed',
                            'time': DateTime("2014-06-20")},
                    )),
            )
    provideUtility(WorkflowSource,
                   name=u'plone.app.transmogrifier.tests.workflowsource')


def browserDefaultSetUp(test):
    sectionsSetUp(test)

    from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

    class MockPortal(MockObjectManager):
        implements(ISelectableBrowserDefault)

        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == '/':
                return False  # path is absolute
            if isinstance(path, unicode):
                return False
            if path == 'not/existing/bar':
                return False
            return True

        updated = []

        def setLayout(self, layout):
            self.updated.append((self._last_path[0], 'layout', layout))

        def setDefaultPage(self, defaultpage):
            self.updated.append(
                (self._last_path[0], 'defaultpage', defaultpage))

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class BrowserDefaultSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(BrowserDefaultSource, self).__init__(*args, **kw)
            self.sample = (
                dict(
                    _path='/spam/eggs/foo',
                    _layout='spam'),
                dict(
                    _path='/spam/eggs/bar',
                    _defaultpage='eggs'),
                dict(
                    _path='/spam/eggs/baz',
                    _layout='spam',
                    _defaultpage='eggs'),
                dict(
                    _path='not/existing/bar',
                    _layout='spam',
                    title='Should not be updated, not an existing path'),
                dict(
                    _path='spam/eggs/incomplete',
                    title='Should not be updated, no layout or defaultpage'),
                dict(
                    _path='spam/eggs/emptylayout',
                    _layout='',
                    title='Should not be updated, no layout or defaultpage'),
                dict(
                    _path='spam/eggs/emptydefaultpage',
                    _defaultpage='',
                    title='Should not be updated, no layout or defaultpage'),
            )
    provideUtility(BrowserDefaultSource,
                   name=u'plone.app.transmogrifier.tests.browserdefaultsource')


def urlNormalizerSetUp(test):
    sectionsSetUp(test)

    from Products.CMFDynamicViewFTI.interface import ISelectableBrowserDefault

    class MockPortal(MockObjectManager):
        implements(ISelectableBrowserDefault)

        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == '/':
                return False  # path is absolute
            if isinstance(path, unicode):
                return False
            if path == 'not/existing/bar':
                return False
            return True

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class URLNormalizerSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(URLNormalizerSource, self).__init__(*args, **kw)
            self.sample = (
                dict(title='mytitle'),
                dict(title='Is this a title of any sort?'),
                dict(title='Put some <br /> $1llY V4LUES -- here&there'),
                dict(title='What about \r\n line breaks (system)'),
                dict(title='Try one of these --------- oh'),
                dict(language='My language is de'),
                dict(language='my language is en')
            )
    provideUtility(URLNormalizerSource,
                   name=u'plone.app.transmogrifier.tests.urlnormalizersource')


def criteriaSetUp(test):
    sectionsSetUp(test)

    from Products.ATContentTypes.interface import IATTopic

    class MockPortal(MockObjectManager):
        implements(IATTopic)

        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == '/':
                return False  # path is absolute
            if isinstance(path, unicode):
                return False
            if path == 'not/existing/bar':
                return False
            return True

        criteria = []

        def addCriterion(self, field, criterion):
            self.criteria.append((self._last_path[0], field, criterion))

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class CriteriaSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(CriteriaSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo', _criterion='bar', _field='baz'),
                dict(_path='not/existing/bar', _criterion='bar', _field='baz',
                     title='Should not be updated, not an existing path'),
                dict(_path='spam/eggs/incomplete',
                     title='Should not be updated, no criterion or field'),
            )
    provideUtility(CriteriaSource,
                   name=u'plone.app.transmogrifier.tests.criteriasource')


def mimeencapsulatorSetUp(test):
    sectionsSetUp(test)

    class EncapsulatorSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(EncapsulatorSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_data='foobarbaz', _mimetype='application/x-test-data'),
                dict(_mimetype='skip/nodata'),
                dict(portrait='skip, no mimetypeset'),
                dict(portrait='someportraitdata',
                     _portrait_mimetype='image/jpeg'),
            )
    provideUtility(EncapsulatorSource,
                   name=u'plone.app.transmogrifier.tests.encapsulatorsource')

    from OFS.Image import File

    class OFSFilePrinter(object):

        """Prints out data on any OFS.Image.File object in the item"""
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, transmogrifier, name, options, previous):
            self.previous = previous

        def __iter__(self):
            for item in self.previous:
                for key, value in item.iteritems():
                    if isinstance(value, File):
                        print '%s: (%s) %s' % (
                            key, value.content_type, str(value))
                yield item
    provideUtility(OFSFilePrinter,
                   name=u'plone.app.transmogrifier.tests.ofsfileprinter')


def uidSetUp(test):
    sectionsSetUp(test)

    from Products.Archetypes.interfaces import IReferenceable

    class MockPortal(MockObjectManager):
        implements(IReferenceable)

        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == '/':
                return False  # path is absolute
            if isinstance(path, unicode):
                return False
            if path == 'not/existing/bar':
                return False
            if path.endswith('/notatcontent'):
                return object()
            return True

        uids_set = []
        _at_uid = 'xyz'

        def UID(self):
            return self._at_uid

        def _setUID(self, uid):
            self.uids_set.append((self._path, uid))
            self._at_uid = uid

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class UIDSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(UIDSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo', _uid='abc',),  # will be set
                dict(_path='/spam/eggs/bar', _uid='xyz',),  # same as default
                dict(_path='not/existing/bar', _uid='def',),  # not found
                dict(_uid='geh',),  # no path
                dict(_path='/spam/eggs/baz',),  # no uid
                dict(
                    _path='/spam/notatcontent',
                    _uid='ijk',
                ),
                # not referenceable
            )
    provideUtility(UIDSource,
                   name=u'plone.app.transmogrifier.tests.uidsource')


def reindexObjectSetup(test):
    sectionsSetUp(test)

    from Products.CMFCore.CMFCatalogAware import CatalogAware
    from Products.Archetypes.interfaces import IBaseObject

    class MockPortal(MockObjectManager, CatalogAware):
        implements(IBaseObject)

        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == '/':
                return False  # path is absolute
            if isinstance(path, unicode):
                return False
            if path == 'not/existing/bar':
                return False
            if path == 'not/a/catalog/aware/content':
                return False
            return True

        @property
        def portal_catalog(self):
            return self

        reindexed = []

        def reindexObject(self, ob):
            self.reindexed.append((self._last_path[0], 'reindexed'))

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class ReindexObjectSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(ReindexObjectSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo'),  # will be set
                dict(_path='/spam/eggs/bar'),  # will be set
                dict(_path='/spam/eggs/baz'),  # will be set
                dict(_path='not/a/catalog/aware/content',
                     title='Should not be reindexed, not a CMFCatalogAware content'),
                dict(_path='not/existing/bar',
                     title='Should not be reindexed, not an existing path'),
            )
    provideUtility(ReindexObjectSource,
                   name=u'plone.app.transmogrifier.tests.reindexobjectsource')


def redirectorSetUp(test):
    sectionsSetUp(test)
    from plone.app.redirector import storage
    from plone.app.redirector import interfaces
    provideUtility(storage.RedirectionStorage(),
                   provides=interfaces.IRedirectionStorage)


def pathfixerSetUp(test):
    sectionsSetUp(test)

    class SchemaSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(SchemaSource, self).__init__(*args, **kw)
            self.sample = (
                dict(_path='/spam/eggs/foo'),
                dict(_path='relative/path'),
                dict(_path='/spam/eggs/another'),
            )
    provideUtility(SchemaSource,
                   name=u'plone.app.transmogrifier.tests.schemasource')


def datesupdaterSetUp(test):
    sectionsSetUp(test)

    class MockPortal(MockObjectManager):

        def hasObject(self, id_):
            path = posixpath.join(self._path, id_)
            if path[0] == '/':
                return False  # path is absolute
            if isinstance(path, unicode):
                return False
            if path == 'not/existing/bar':
                return False
            return True

        updated = []

        @property
        def creation_date(self):
            return DateTime()

        @creation_date.setter
        def creation_date(self, val):
            self.updated.append((self._last_path[0], 'creation_date', val))

        @property
        def modification_date(self):
            return DateTime()

        @modification_date.setter
        def modification_date(self, val):
            self.updated.append((self._last_path[0], 'modification_date', val))

    test.globs['plone'] = MockPortal()
    test.globs['transmogrifier'].context = test.globs['plone']

    class SchemaSource(SampleSource):
        classProvides(ISectionBlueprint)
        implements(ISection)

        def __init__(self, *args, **kw):
            super(SchemaSource, self).__init__(*args, **kw)
            self.sample = (
                dict(
                    _path='/spam/eggs/foo',
                    creation_date=DateTime(2010, 10, 10),
                    modification_date=DateTime(2012, 12, 12),
                ),
                dict(  # only creation date updated
                    _path='/spam/eggs/bar',
                    creation_date=DateTime(2010, 10, 10),
                ),
                dict(  # only modification date updated
                    _path='/spam/eggs/baz',
                    modification_date=DateTime(2012, 12, 12),
                ),
                dict(  # Should not be updated, not an existing path
                    _path='not/existing/bar',
                    creation_date=DateTime(2010, 10, 10),
                    modification_date=DateTime(2012, 12, 12),
                ),
                dict(  # Should not be updated, no path
                    creation_date=DateTime(2010, 10, 10),
                    modification_date=DateTime(2012, 12, 12),
                )
            )
    provideUtility(SchemaSource,
                   name=u'plone.app.transmogrifier.tests.schemasource')


def test_suite():
    return unittest.TestSuite((
        doctest.DocFileSuite(
            'portaltransforms.rst',
            optionflags=optionflags,
            setUp=portalTransformsSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'atschemaupdater.rst',
            optionflags=optionflags,
            setUp=aTSchemaUpdaterSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'uidupdater.rst',
            optionflags=optionflags,
            setUp=uidSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'workflowupdater.rst',
            optionflags=optionflags,
            setUp=workflowUpdaterSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'browserdefault.rst',
            optionflags=optionflags,
            setUp=browserDefaultSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'urlnormalizer.rst',
            optionflags=optionflags,
            setUp=urlNormalizerSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'criteria.rst',
            optionflags=optionflags,
            setUp=criteriaSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'mimeencapsulator.rst',
            optionflags=optionflags,
            setUp=mimeencapsulatorSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'reindexobject.rst',
            optionflags=optionflags,
            setUp=reindexObjectSetup, tearDown=tearDown),
        doctest.DocFileSuite(
            'redirector.rst',
            optionflags=doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF,
            setUp=redirectorSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'pathfixer.rst',
            optionflags=optionflags,
            setUp=pathfixerSetUp, tearDown=tearDown),
        doctest.DocFileSuite(
            'datesupdater.rst',
            optionflags=optionflags,
            setUp=datesupdaterSetUp, tearDown=tearDown),
    ))
