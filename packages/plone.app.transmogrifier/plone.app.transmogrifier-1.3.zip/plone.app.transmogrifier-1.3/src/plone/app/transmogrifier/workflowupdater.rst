Workflow updater section
------------------------

A workflow updater pipeline section is another important transmogrifier content
import pipeline element. It executes workflow transitions on Plone content
based on the items it processes. The workflow updater section blueprint name is
``plone.app.transmogrifier.workflowupdater``. Workflow updater sections operate
on objects already present in the ZODB, be they created by a constructor or
pre-existing objects.

Workflow updating needs 2 pieces of information: the path to the object, and
what transitions to execute. To determine these, the workflow updater section
inspects each item and looks for two keys, as described below. Any item missing
any of these two pieces will be skipped. Similarly, items with a path that
doesn't exist will be skipped as well.

For the object path, it'll look (in order) for
``_plone.app.transmogrifier.atschemaupdater_[sectionname]_path``,
``_plone.app.transmogrifier.atschemaupdater_path``, ``_[sectionname]_path`` and
``_path``, where ``[sectionname]`` is replaced with the name given to the
current section. This allows you to target the right section precisely if
needed. Alternatively, you can specify what key to use for the path by
specifying the ``path-key`` option, which should be a list of keys to try (one
key per line, use a ``re:`` or ``regexp:`` prefix to specify regular
expressions).

For the transitions, use the ``transitions-key`` option (same interpretation
as ``path-key``), defaulting to
``_plone.app.transmogrifier.atschemaupdater_[sectionname]_transitions``,
``_plone.app.transmogrifier.atschemaupdater_transitions``,
``_[sectionname]_transitions`` and ``_transitions``.

Unicode paths are encoded to ASCII. Paths to objects are always interpreted as
relative to the context object. Transitions are specified as a sequence of
transition names, or as a string specifying one transition, or a list of
dictionaries containing 'action' as transition id, 'review_state' as state id
and 'time' as a DateTime representing the transition time (if so, the worflow
history will be updated with the provided date). Transitions are executed in
order, failing transitions are silently ignored.

::

    >>> import pprint
    >>> workflow = """
    ... [transmogrifier]
    ... pipeline =
    ...     workflowsource
    ...     workflowupdater
    ...     printer
    ...     
    ... [workflowsource]
    ... blueprint = plone.app.transmogrifier.tests.workflowsource
    ... 
    ... [workflowupdater]
    ... blueprint = plone.app.transmogrifier.workflowupdater
    ... 
    ... [printer]
    ... blueprint = collective.transmogrifier.sections.logger
    ... name = logger
    ... """
    >>> registerConfig(u'plone.app.transmogrifier.tests.workflow',
    ...                workflow)
    >>> transmogrifier(u'plone.app.transmogrifier.tests.workflow')
    >>> print(handler)
    logger INFO
      {'_path': '/spam/eggs/foo', '_transitions': 'spam'}
    logger INFO
      {'_path': '/spam/eggs/baz', '_transitions': ('spam', 'eggs')}
    logger INFO
        {'_path': 'not/existing/bar',
       '_transitions': ('spam', 'eggs'),
       'title': 'Should not be updated, not an existing path'}
    logger INFO
        {'_path': 'spam/eggs/incomplete',
       'title': 'Should not be updated, no transitions'}
    logger INFO
        {'_path': '/spam/eggs/nosuchtransition',
       '_transitions': ('nonsuch',),
       'title': 'Should not be updated, no such transition'}
    logger INFO
        {'_path': '/spam/eggs/bla',
       '_transitions': ({'action': 'spam',
                         'review_state': 'spammed',
                         'time': DateTime('2014/06/20 00:00:00 GMT+0')},)}

    >>> pprint.pprint(plone.updated)
    [('spam/eggs/foo', 'spam'),
     ('spam/eggs/baz', 'spam'),
     ('spam/eggs/baz', 'eggs'),
     ('spam/eggs/bla', 'spam')]
