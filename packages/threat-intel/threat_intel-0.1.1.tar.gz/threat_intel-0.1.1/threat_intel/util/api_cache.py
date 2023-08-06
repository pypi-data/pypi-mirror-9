# -*- coding: utf-8 -*-
#
# ApiCache creates an on disk cache of API call results
#
import simplejson
from simplejson.scanner import JSONDecodeError


class ApiCache(object):

    """creates an on disk cache of API call results."""

    def __init__(self, cache_file_name):
        """Opens the cache file and reads previous results.

        Args:
                cache_file_name: string file name
        """
        self._cache_file_name = cache_file_name
        self._cache = self._read_cache_from_file()

    def __del__(self):
        """Ensures cache is persisted to disk before object is destroyed.

        Using a destructor is a bit inflammatory but it seems like a very nice way to write a file when "everything is done".
        The ApiCache avoids circular dependencies so it should work out.
        """
        self.close()

    def close(self):
        """Write the contents of the cache to disk and clear the in memory cache."""
        if self._cache:
            self._write_cache_to_file()
            self._cache = None

    def _write_cache_to_file(self):
        """Write the contents of the cache to a file on disk."""
        with(open(self._cache_file_name, 'w')) as fp:
            fp.write(simplejson.dumps(self._cache))

    def _read_cache_from_file(self):
        """Read the contents of the cache from a file on disk."""
        cache = {}
        try:
            with(open(self._cache_file_name, 'r')) as fp:
                contents = fp.read()
                cache = simplejson.loads(contents)
        except (IOError, JSONDecodeError):
            # The file could not be read. This is not a problem if the file does not exist.
            pass

        return cache

    def cache_value(self, api_name, key, value):
        """Add the value of an API call to the cache.

        Args:
            api_name: a string name of the API. Keys and values are segmented by api_name.
            key: a string key for the specific call.
            value: the value of the call using the specific key
        """
        self._cache.setdefault(api_name, {})
        self._cache[api_name][key] = value

    def lookup_value(self, api_name, key):
        """Add the value of an API call to the cache.

        Args:
            api_name: a string name of the API. Keys and values are segmented by api_name.
            key: a string key for the specific call.
        """
        if api_name in self._cache:
            return self._cache[api_name].get(key, None)
        return None

    def bulk_lookup(self, api_name, keys):
        """Perform lookup on an enumerable of keys.

        Args:
            api_name: a string name of the API. Keys and values are segmented by api_name.
            keys: an enumerable of string keys.
        """
        cached_data = {}

        for key in keys:
            value = self.lookup_value(api_name, key)
            if value is not None:
                cached_data[key] = value
        return cached_data
