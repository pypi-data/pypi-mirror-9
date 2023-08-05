from collections import defaultdict
import openerp_proxy.orm.record
__all__ = ('empty_cache')


class ObjectCache(defaultdict):
    """ Simple wrapper to also store Record instances in cache, so no need to create new ones
    """
    def __init__(self, root, obj, *args, **kwargs):
        self._root_cache = root
        self._object = obj
        self._records = {}
        self._fields = set(['id'])
        super(ObjectCache, self).__init__(dict, *args, **kwargs)

    @property
    def fields(self):
        return self._fields

    @property
    def records(self):
        return self._records

    def get_record(self, rid):
        record = self._records.get(rid, None)
        if record is None:
            record = self._records[rid] = openerp_proxy.orm.record.Record(self._object, rid, cache=self._root_cache)
        return record


class Cache(dict):
    """ Cache to be used for Records
    """
    def __init__(self, proxy, *args, **kwargs):
        self._proxy = proxy
        super(Cache, self).__init__(*args, **kwargs)

    def __missing__(self, key):
        try:
            obj = self._proxy.get_obj(key)
        except ValueError:
            raise KeyError("There are not object with such name: %s" % key)
        lcache = self[key] = ObjectCache(self, obj)
        return lcache


def empty_cache(proxy):
    """ Created instance of empty cache for Record

        Ususaly cache will be dictionary structure like::

            cache = {
                'product.product': {
                    1: {
                        'id': 1,
                        'name': 'product1',
                        'default_code': 'product1',
                    },
                    ...
                },
                ...
            }
    """
    #return defaultdict(lambda: defaultdict(dict))
    return Cache(proxy)


