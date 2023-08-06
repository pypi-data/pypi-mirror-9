from zope import schema
from zope.interface import Interface

from zope.container.interfaces import IOrderedContainer, \
    IContainerNamesContainer

from plone.directives import form
from plone.app.textfield import RichText
from plone.app.z3cform.widget import DatetimeFieldWidget
from plone.formwidget.autocomplete import AutocompleteMultiFieldWidget

from plone.theme.interfaces import IDefaultPloneLayer


class INoticesLayer(IDefaultPloneLayer):
    """A layer specific for collective.notices.
    """


class INoticesStorage(IOrderedContainer, IContainerNamesContainer): pass


class INotice(form.Schema):

    text = RichText(title=u"Text", required=True)

    form.widget(users_and_groups=AutocompleteMultiFieldWidget)
    users_and_groups = schema.List(
        title=u"Users and groups",
        value_type=schema.Choice(
            title=u"Selection",
            vocabulary="plone.principalsource.Principals"
        ),
        required=False,
        default=[],
    )

    form.widget(effective_date=DatetimeFieldWidget)
    effective_date = schema.Datetime(title=u'Effective Date', required=False, default=None)
    
    form.widget(expiration_date=DatetimeFieldWidget)
    expiration_date = schema.Datetime(title=u'Expiration Date', required=False, default=None)

    active = schema.Bool(title=u'Active', default=True)


class ICatalogFactory(Interface):
    """Factory for the catalog used for notices.
    """
    
    def __call__():
        """Create and return the Catalog.
        
        @param return: zope.catalog.catalog.Catalog instance
        """


class INoticesQuery(Interface): pass


class INoticeFactory(Interface):
    """Factory for notices.
    """
    
    def __call__(**kwargs):
        """Create and return the notice.
        """
