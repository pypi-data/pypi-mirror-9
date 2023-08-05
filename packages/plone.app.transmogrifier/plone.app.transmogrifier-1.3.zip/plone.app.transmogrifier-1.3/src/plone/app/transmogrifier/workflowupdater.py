from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFCore.utils import getToolByName
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import traverse
from zope.interface import classProvides, implements

# XXX Weird things may happen if you have multiple workflows.
# Needs investigating and solving //regebro


class WorkflowUpdaterSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.wftool = getToolByName(self.context, 'portal_workflow')

        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.transitionskey = defaultMatcher(options, 'transitions-key', name,
                                             'transitions')

    def __iter__(self):
        for item in self.previous:
            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]
            transitionskey = self.transitionskey(*keys)[0]

            if not (pathkey and transitionskey):  # not enough info
                yield item
                continue

            path, transitions = item[pathkey], item[transitionskey]
            if isinstance(transitions, basestring):
                transitions = (transitions,)

            obj = traverse(self.context, str(path).lstrip('/'), None)
            if obj is None:                      # path doesn't exist
                yield item
                continue

            for transition in transitions:
                if not isinstance(transition, basestring):
                    state = transition['review_state']
                    time = transition['time']
                    action = transition.get('action')
                    # no action if initial state
                    if action:
                        try:
                            self.wftool.doActionFor(obj, action)
                        except WorkflowException:
                            pass
                    history = getattr(obj, 'workflow_history', None)
                    if history:
                        for wf in history:
                            for wf_state in history[wf]:
                                if wf_state['review_state'] == state:
                                    wf_state['time'] = time
                        obj.workflow_history = history
                else:
                    try:
                        self.wftool.doActionFor(obj, transition)
                    except WorkflowException:
                        pass

            yield item
