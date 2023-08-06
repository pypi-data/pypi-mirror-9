import json

from zope.component import getUtility
from zope.container.interfaces import INameChooser
from zope.app.component.hooks import getSite
from zope.cachedescriptors.property import Lazy

from z3c.form import button
from plone.directives import form

from plone.batching import Batch
from plone.z3cform.crud.crud import CrudBatchView

from five import grok

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

from zope.lifecycleevent import ObjectRemovedEvent
from zope.event import notify

from ..interfaces import INotice, INoticesStorage, INoticeFactory, \
    INoticesLayer
from ..catalog import ResultSet


grok.layer(INoticesLayer)


class AddNotice(form.SchemaAddForm):
    
    grok.context(INoticesStorage)
    grok.require('cmf.ManagePortal')
    grok.name('add')
    
    schema = INotice
    
    label = u"Add Notice"
    
    def create(self, data):
        return INoticeFactory(self.context)(**data)

    def add(self, ob):
        self.context[INameChooser(self.context).chooseName()] = ob


class EditNotice(form.SchemaEditForm):

    grok.context(INotice)
    grok.require('cmf.ManagePortal')
    grok.name('edit')
    
    schema = INotice

    label = u"Edit Notice"

    def __init__(self, *args, **kwargs):
        super(EditNotice, self).__init__(*args, **kwargs)
        self.request.set('disable_border', True)
    
    @button.buttonAndHandler(u'Save', name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(u"Changes saved", "info")
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(u'Cancel', name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(u"Edit cancelled", "info")
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return getSite().absolute_url() + '/++notices++'


class DeleteNotice(grok.View):
    
    grok.context(INotice)
    grok.require('cmf.ManagePortal')
    grok.name('delete')

    def render(self):
        event = ObjectRemovedEvent(self.context, self.context.__parent__,
                                   self.context.__name__)
        notify(event)
        del self.context.__parent__[self.context.__name__]
        IStatusMessage(self.request).addStatusMessage(u"Item deleted", "info")
        self.request.response.redirect(self.nextURL())

    def nextURL(self):
        return getSite().absolute_url() + '/++notices++'


class HideNotice(grok.View):
    
    grok.context(ISiteRoot)
    grok.require('zope2.View')
    grok.name('hide-notice')

    def render(self):
        id = int(self.request.get('id', 0))
        cookie_name = 'hidden-notices-' + self.cookieSuffix()
        try:
            hidden = set(json.loads(self.request.get(cookie_name, '[]')))
        except (TypeError, ValueError):
            hidden = set()
        if id:
            hidden.add(id)
            storage = getUtility(INoticesStorage)
            hidden = [id for id in hidden if unicode(id) in storage]
            self.request.response.setCookie(cookie_name, json.dumps(hidden))

        if self.request.form.get('ajax') == '1':
            return 'success'
        else:
            return self.request.response.redirect(self.request['HTTP_REFERER'])

    def cookieSuffix(self):
        membership = getToolByName(self.context, 'portal_membership', None)
        member = membership.getAuthenticatedMember()
        if not member:
            return 'anonymous'
        return member.getId() or 'anonymous'


class ManageNotices(grok.View):
    
    grok.context(INoticesStorage)
    grok.require('cmf.ManagePortal')
    grok.name('manage')

    @Lazy
    def notices(self):
        return ResultSet(self.context.keys(), self.context)

    @Lazy
    def batch(self):
        batch_size = 10
        page = int(self.request.get('page', '0'))
        return Batch(self.notices, start=page*batch_size, size=batch_size)

    def render_batch_navigation(self):
        navigation = CrudBatchView(self.batch, self.request)
        return navigation()

