

import collections
import functools

import cPickle
import errno
import logging
import os
import re
import sys
import time

from termcolor import cprint

from mad2.exception import MadPermissionDenied, MadNotAFile
from mad2.madfile import MadFile, MadDummy

import fantail


lg = logging.getLogger(__name__)
#lg.setLevel(logging.DEBUG)

STORES = None


def persistent_cache(path, cache_on, duration):
    """
    Disk persistent cache that reruns a function once every
    'duration' no of seconds
    """
    def decorator(original_func):

        def new_func(*args, **kwargs):

            if isinstance(cache_on, str):
                cache_name = kwargs[cache_on]
            elif isinstance(cache_on, int):
                cache_name = args[cache_on]

            full_cache_name = os.path.join(path, cache_name)
            lg.debug("cache file: %s", full_cache_name)
            run = False

            if kwargs.get('force'):
                run = True

            if not os.path.exists(full_cache_name):
                #file does not exist. Run!
                run = True
            else:
                #file exists - but is it more recent than
                #duration (in seconds)
                mtime = os.path.getmtime(full_cache_name)
                age = time.time() - mtime
                if age > duration:
                    lg.debug("Cache file is too recent")
                    lg.debug("age: %d", age)
                    lg.debug("cache refresh: %d", duration)
                    run = True

            if not run:
                #load from cache
                lg.debug("loading from cache: %s", full_cache_name)
                with open(full_cache_name) as F:
                    res = cPickle.load(F)
                    return res


            #no cache - create
            lg.debug("no cache - running function %s", original_func)
            rv = original_func(*args, **kwargs)
            lg.debug('write to cache: %s', full_cache_name)

            if not os.path.exists(path):
                os.makedirs(path)
            with open(full_cache_name, 'wb') as F:
                cPickle.dump(rv, F)

            return rv

        return new_func

    return decorator


def boolify(v):
    """
    return a boolean from a string
    yes, y, true, True, t, 1 -> True
    otherwise -> False
    """
    return v.lower() in ['yes', 'y', 'true', 't', '1']


def message(cat, message, *args):
    if len(args) > 0:
        message = message.format(*args)

    message = " ".join(message.split())
    color = {'er': 'red',
             'wa': 'yellow',
             'in': 'green',
             }.get(cat.lower()[:2], 'blue')

    cprint('Kea', 'cyan', end="/")
    cprint(cat, color)
    for line in textwrap.wrap(message):
        print "  " + line


        
# Borrowed from: http://tinyurl.com/majcr53
class memoized(object):

    '''Decorator. Caches a function's return value each time it is called.
    If called later with the same arguments, the cached value is returned
    (not reevaluated).
    '''

    def __init__(self, func):
        self.func = func
        self.cache = {}

    def __call__(self, *args):
        if not isinstance(args, collections.Hashable):
            # uncacheable. a list, for instance.
            # better to not cache than blow up.
            return self.func(*args)
        if args in self.cache:
            return self.cache[args]
        else:
            value = self.func(*args)
            self.cache[args] = value
            return value

    def __repr__(self):
        '''Return the function's docstring.'''
        return self.func.__doc__

    def __get__(self, obj, objtype):
        '''Support instance methods.'''
        return functools.partial(self.__call__, obj)

