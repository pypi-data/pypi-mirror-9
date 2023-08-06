import random

from zope.interface import implements
from zope.component import getUtility
from zope.schema.fieldproperty import FieldProperty
from zope.container.contained import Contained, NameChooser
from zope.container.interfaces import INameChooser
from zope.lifecycleevent.interfaces import (
    IObjectAddedEvent, IObjectModifiedEvent, IObjectRemovedEvent)

from OFS.SimpleItem import SimpleItem

from five import grok

from .interfaces import INotice, INoticesStorage, INoticeFactory


class Notice(SimpleItem, Contained):

    implements(INotice)

    __name__ = u''

    active = FieldProperty(INotice['active'])
    
    effective_date = FieldProperty(INotice['effective_date'])
    
    expiration_date = FieldProperty(INotice['expiration_date'])
    
    text = FieldProperty(INotice['text'])
    
    users_and_groups = FieldProperty(INotice['users_and_groups'])

    def __init__(self, text=u'', active=True, users_and_groups=[],
                 effective_date=None, expiration_date=None):
        super(Notice, self).__init__()
        self.text = text
        self.active = active
        self.users_and_groups = users_and_groups
        self.effective_date = effective_date
        self.expiration_date = expiration_date
    
    @property
    def id(self):
        return self.__name__


class NoticeNameChooser(grok.Adapter, NameChooser):
    """A name chooser for notices.
    """

    grok.context(INoticesStorage)
    grok.provides(INameChooser)

    _v_nextid = None

    def chooseName(self, *args, **kwargs):
        while True:
            if self._v_nextid is None:
                self._v_nextid = random.randrange(0, 2**31)
            uid = self._v_nextid
            self._v_nextid += 1
            if uid not in self.context:
                return unicode(uid)
            self._v_nextid = None


class NoticeFactory(grok.Adapter):
    """A factory for notices.
    """

    grok.context(INoticesStorage)
    grok.provides(INoticeFactory)

    def __call__(self, **kwargs):
        return Notice(**kwargs)


@grok.subscribe(INotice, IObjectAddedEvent)
def noticeAdded(obj, event):
    storage = getUtility(INoticesStorage)
    storage.catalog.index_doc(int(obj.__name__), obj)


@grok.subscribe(INotice, IObjectModifiedEvent)
def noticeModified(obj, event):
    storage = getUtility(INoticesStorage)
    storage.catalog.index_doc(int(obj.__name__), obj)


@grok.subscribe(INotice, IObjectRemovedEvent)
def noticeRemoved(obj, event):
    storage = getUtility(INoticesStorage)
    storage.catalog.unindex_doc(int(obj.__name__))
