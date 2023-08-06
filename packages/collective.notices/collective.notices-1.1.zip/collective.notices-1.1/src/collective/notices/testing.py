from Products.CMFCore.utils import getToolByName

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from zope.configuration import xmlconfig

class CollectiveNotices(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    MEMBER_NAME = 'janedoe'
    MEMBER_PASSWORD = 'secret'
    MANAGER_USER_NAME = 'manager'
    MANAGER_USER_PASSWORD = 'secret'
    
    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import plone.principalsource
        self.loadZCML(package=plone.principalsource)
        import plone.formwidget.autocomplete
        self.loadZCML(package=plone.formwidget.autocomplete)
        import collective.notices
        xmlconfig.file('configure.zcml', 
                       collective.notices, 
                       context=configurationContext)

    def setUpPloneSite(self, portal):
        # Install into Plone site using portal_setup
        applyProfile(portal, 'collective.notices:default')

        # Creates some users
        acl_users = getToolByName(portal, 'acl_users')
        acl_users.userFolderAddUser(
            self.MEMBER_NAME,
            self.MEMBER_PASSWORD,
            ['Member'],
            [],
        )
        acl_users.userFolderAddUser(
            self.MANAGER_USER_NAME,
            self.MANAGER_USER_PASSWORD,
            ['Manager'],
            [],
        )

COLLECTIVE_NOTICES_FIXTURE = CollectiveNotices()
COLLECTIVE_NOTICES_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_NOTICES_FIXTURE,), 
    name="CollectiveNotices:Integration")
COLLECTIVE_NOTICES_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_NOTICES_FIXTURE,), 
    name="CollectiveNotices:Functional")
