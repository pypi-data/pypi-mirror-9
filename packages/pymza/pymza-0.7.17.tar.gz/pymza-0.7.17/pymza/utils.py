import time
import collections
import functools


class ExponentialSleep(object):

    def __init__(self, initial=0.1, max=10, multiplier=2.0):
        self.initial = initial
        self.max = max
        self.multiplier = multiplier
        self.num_sleeps = 0
        self.reset()

    def reset(self):
        self.current = self.initial
        self.num_sleeps = 0

    def sleep(self):
        time.sleep(self.current)
        self.current = min(self.current * self.multiplier, self.max)
        self.num_sleeps += 1


class IntervalTracker(object):

    def __init__(self, interval):
        self.interval = interval
        self.last_triggered = time.time()

    def __nonzero__(self):
        return self.is_triggered()

    def is_triggered(self):
        now = time.time()
        return now >= self.last_triggered + self.interval

    def reset(self):
        self.last_triggered = time.time()


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
