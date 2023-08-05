import sys
import time
import greenlet
import gevent.hub

MAX_BLOCKING_TIME = 0.5
_last_switch_time = None


class GeventBlockingTracker(object):
    def __init__(self, max_blocking_time):
        self.max_blocking_time = max_blocking_time
        self.last_switch_time = None

    def __call__(self, what, (origin, target)):
        then = self.last_switch_time
        now = self.last_switch_time = time.time()
        if then is not None:
            blocking_time = now - then
            if origin is not gevent.hub.get_hub():
                if blocking_time > MAX_BLOCKING_TIME:
                    msg = ">>>>>>>>>>>>>>>>>>> Greenlet %s blocked the eventloop for %.4f seconds\n"
                    msg = msg % (origin, blocking_time, )
                    print >> sys.stderr, msg

    @classmethod
    def track(cls, max_blocking_time):
        greenlet.settrace(cls(max_blocking_time))
