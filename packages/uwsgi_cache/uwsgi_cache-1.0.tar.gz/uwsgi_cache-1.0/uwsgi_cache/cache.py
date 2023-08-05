try:
    import uwsgi
except:
    pass
import json

# use cPickle for speed
import cPickle as pickle

class CacheManager(object):
    """
    uWSGI CacheManger

    This cache manager allows the use of various clearable named caches.
    it stores state data in a cache key named cache|name
    """
    def __init__(self, name, expires):
        """
        Build a CacheManager instance

        :params:
            name: the name of the cache that you would like to create
            expires: the expire time of the cache data
        :returns:
            a CacheManager object
        """
        self.__name__ = "cache|{}".format(name)
        self.expires = expires

    def __ensure_exist__(self):
        """
        Internal function to ensure that the cache mangager internal accounting has
        been created
        """
        if not uwsgi.cache_exists(self.__name__):
            obj = { "keys": [] }
            uwsgi.cache_set(self.__name__, json.dumps(obj))

    def __load_obj__(self):
        """
        Internal function to load the cache manager state data
        """
        self.__ensure_exist__()
        value = uwsgi.cache_get(self.__name__)
        if not value:
            return None
        return json.loads(value)

    def __save_obj__(self, obj):
        """
        Internal function to save the cache manager state data
        """
        self.__ensure_exist__()
        uwsgi.cache_update(self.__name__, json.dumps(obj))

    def __get__key__(self, key):
        """
        Internal function to build a local key name
        """
        return "{}|data|{}".format(self.__name__, key)

    def __key_exists__(self, key):
        """
        Internal function to lookup a key within the state object
        """
        obj = self.__load_obj__()
        if not obj or 'keys' not in obj:
            return False
        return key in obj['keys'] and uwsgi.cache_exists(self.__get__key__(key))

    def __add_key__(self, key):
        """
        Internal function to add a key to the internal state object
        """
        obj = self.__load_obj__()
        if not obj or 'keys' not in obj:
            return None

        if key not in obj['keys']:
            obj['keys'].append(key)
        self.__save_obj__(obj)

    def is_fake(self):
        """
        Function to determine if the cache is fake

        The cache is fake if running without a cache configured in uwsgi
        """
        self.__ensure_exist__()
        obj = self.__load_obj__()
        return obj == None

    def keys(self):
        """
        Return a list of all the keys in the cache object
        """
        obj = self.__load_obj__()
        if obj and 'keys' in obj:
            return obj['keys']

    def exists(self, key):
        """
        Return true if the key exists in the cache
        """
        return self.__key_exists__(key) and uwsgi.cache_exists(self.__get__key__(key))

    def set(self, key, value):
        """
        Set key to value in the cache
        """
        data = pickle.dumps(value)
        if self.__key_exists__(key):
            uwsgi.cache_update(self.__get__key__(key), data, self.expires)
        else:
            self.__add_key__(key)
            uwsgi.cache_set(self.__get__key__(key), data, self.expires)

    def get(self, key):
        """
        Return the value associated with key
        """
        if self.__key_exists__(key):
            return pickle.loads(uwsgi.cache_get(self.__get__key__(key)))

    def delete(self, key):
        """
        Delete a key from the cache
        """
        if self.__key_exists__(key):
            return uwsgi.cache_del(self.__get__key__(key))

    def clear(self):
        """
        Clear this named cache area
        """
        obj = self.__load_obj__()
        if self.is_fake():
            return None

        for key in obj['keys']:
            uwsgi.cache_del(self.__get__key__(key))

        obj['keys'] = []
        self.__save_obj__(obj)

    def clear_uwsgi_cache(self):
        """
        Clear ENTIRE uwsgi cache

        You probably dont need this
        """
        uwsgi.cache_clear()

class Cacher(object):
    """
    Cacher
    ------

    This class should be used to create a named cache around this cache manager

    The cache method will cache the results of a function

    The invalidate method will clear out all the results within that cache
    """
    def __init__(self, name, expires):
        self.cache_obj = CacheManager(name, expires)

    def cache(self):
        def wrapper(fn):
            def wrapped(*args, **kwargs):
                key = "|".join(map(str, [fn, args, kwargs]))
                if not self.cache_obj.exists(key):
                    result = fn(*args, **kwargs)
                    self.cache_obj.set(key, result)
                    return result
                else:
                    return self.cache_obj.get(key)
            return wrapped
        return wrapper

    def invalidate(self):
        self.cache_obj.clear()
