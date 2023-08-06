import json

from zope.interface import Interface
from zope.component import getUtility

from five import grok

from plone.app.layout.viewlets.interfaces import IPortalTop

from Products.CMFCore.utils import getToolByName

from ..interfaces import INoticesQuery, INoticesLayer


grok.layer(INoticesLayer)


class NoticesViewlet(grok.Viewlet):
    """Displays notices.
    """

    grok.name('collective.notices')
    grok.context(Interface)
    grok.require('zope2.View')
    grok.viewletmanager(IPortalTop)

    def update(self):
        cookie_name = 'hidden-notices-' + self.cookieSuffix()
        hidden = self.request.get(cookie_name, '[]')
        try:
            hidden = [id for id in json.loads(hidden) if isinstance(id, int)]
        except (ValueError, TypeError):
            hidden = []
        self.notices = list(getUtility(INoticesQuery).filter(
            self.getPrincipalIds(),
            hidden
        ))

    def getPrincipalIds(self):
        
        membership = getToolByName(self.context, 'portal_membership', None)
        if membership is None or membership.isAnonymousUser():
            return ()
        
        member = membership.getAuthenticatedMember()
        if not member:
            return ()
        
        groups = hasattr(member, 'getGroups') and member.getGroups() or []

        # Ensure we get the list of ids - getGroups() suffers some acquision
        # ambiguity - the Plone member-data version returns ids.

        for group in groups:
            if not isinstance(group, basestring):
                return ()
        
        return [member.getId()] + groups

    def cookieSuffix(self):
        membership = getToolByName(self.context, 'portal_membership', None)
        member = membership.getAuthenticatedMember()
        if not member:
            return 'anonymous'
        return member.getId() or 'anonymous'
