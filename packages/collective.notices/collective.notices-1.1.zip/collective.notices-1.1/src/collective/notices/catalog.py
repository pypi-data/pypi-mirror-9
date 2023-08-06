from datetime import datetime

from dateutil.tz import gettz

from BTrees.IFBTree import weightedIntersection, union, difference, IFSet

from zope.component import getUtility
from zope.catalog.catalog import Catalog

from zc.catalog.catalogindex import SetIndex, ValueIndex, DateTimeValueIndex

from five import grok

from .interfaces import ICatalogFactory, INoticesStorage, INotice, INoticesQuery


class ResultSet:
    """Lazily accessed set of objects."""

    def __init__(self, uids, storage):
        self.uids = uids
        self.storage = storage

    def __len__(self):
        return len(self.uids)

    def __iter__(self):
        for uid in self.uids:
            obj = self.storage[unicode(uid)]
            yield obj
    
    def __getslice__(self, *args, **kwargs):
        uids = self.uids.__getslice__(*args, **kwargs)
        return self.__class__(uids, self.storage)


class NoticesQuery(grok.GlobalUtility):

    grok.provides(INoticesQuery)

    @staticmethod
    def intersection(a, b):
        _, res = weightedIntersection(a or IFSet(), b or IFSet())
        return res
    
    @staticmethod
    def union(a, b):
        if a and b:
            return union(a, b)
        return a or b or IFSet()

    difference = staticmethod(difference)

    def filter(self, users_and_groups=None, excluded=None):
        
        now = datetime.now(gettz())
        storage = getUtility(INoticesStorage)
        catalog = storage.catalog
        
        # filter out inactive items
        active_index = catalog['active']
        result = active_index.apply(dict(any_of=(True,))) or IFSet()
        
        all = IFSet(active_index.ids())
        
        users_and_groups_index = catalog['users_and_groups']
        if users_and_groups:
            # filter users and groups
            result = self.intersection(
                result,
                self.union(
                    users_and_groups_index.apply(dict(any_of=users_and_groups)),
                    self.difference(all, IFSet(users_and_groups_index.ids())) # None value
                )
            )
        else:
            # keep only global notices
            result = self.intersection(
                result,
                self.difference(all, IFSet(users_and_groups_index.ids())) # None value
            )
        
        effective_date_index = catalog['effective_date']
        result = self.intersection(
            result,
            self.union(
                effective_date_index.apply(dict(between=(None, now))), # date > now
                self.difference(all, IFSet(effective_date_index.ids())) # None value
            )
        )
        
        expiration_date_index = catalog['expiration_date']
        result = self.intersection(
            result,
            self.union(
                expiration_date_index.apply(dict(between=(now,))), # date < now
                self.difference(all, IFSet(expiration_date_index.ids())) # None value
            )
        )
        
        # filter out excluded notices
        if excluded:
            result = self.difference(result, IFSet(excluded))
        
        return ResultSet(result, storage)


class CatalogFactory(grok.Adapter):
    
    grok.context(INoticesStorage)
    grok.provides(ICatalogFactory)

    indexes = dict(
        active=ValueIndex,
        effective_date=DateTimeValueIndex,
        expiration_date=DateTimeValueIndex,
        users_and_groups=SetIndex,
    )

    def __call__(self):
        catalog = Catalog()
        for attr, idx_factory in self.indexes.iteritems():
            catalog[attr] = idx_factory(attr, INotice)
        return catalog
