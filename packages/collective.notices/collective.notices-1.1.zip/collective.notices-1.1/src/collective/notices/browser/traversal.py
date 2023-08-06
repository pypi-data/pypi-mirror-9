from zope.component import getUtility
from zope.app.component.hooks import getSite

from zope.traversing.interfaces import ITraversable
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces import NotFound
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.container.traversal import ContainerTraverser

from five import grok

from Acquisition import aq_base

from Products.CMFCore.interfaces import ISiteRoot

from ..interfaces import INoticesStorage


class NoticesNamespace(grok.MultiAdapter):
    """Used to traverse to a notice.
    """
    
    grok.adapts(ISiteRoot, IHTTPRequest)
    grok.provides(ITraversable)
    grok.name('notices')

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        storage = aq_base(getUtility(INoticesStorage)).__of__(getSite())
        if storage.__name__ != storage.id != u'++notices++':
            storage.__name__ = storage.id = u'++notices++'
        return storage


class NoticesStorageTraverser(ContainerTraverser, grok.MultiAdapter):
    """A traverser for INoticesStorage, that is acqusition-aware
    """
    
    grok.adapts(INoticesStorage, IBrowserRequest)
    grok.provides(IBrowserPublisher)

    def publishTraverse(self, request, name):
        try:
            ob = ContainerTraverser.publishTraverse(self, request, name)
        except NotFound:
            # workaround to traverse to resources
            return getattr(self.context.aq_parent, name)
        else:
            return ob.__of__(self.context)

    def browserDefault(self, request):
        return self.context, ('@@manage',)
