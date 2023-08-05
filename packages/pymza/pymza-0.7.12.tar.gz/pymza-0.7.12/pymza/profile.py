import sys
import greenlet
import gevent
from collections import defaultdict, Counter
import ctypes, os

import cffi
 
CDEFS = """
double clock_gettime_cpu();
"""
 
CSRC = """
#include <time.h>


double
clock_gettime_cpu()
{
    struct timespec         ts;
    double                  result;

    if ((clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &ts)) < 0) {
        perror("clock_gettime");
        exit(1);
    }

    result = ts.tv_sec + ts.tv_nsec * pow(10, -9);
    return (result);
}
"""
 
ffi = cffi.FFI()
ffi.cdef(CDEFS)
our_lib = ffi.verify(CSRC)
 
clock_gettime_cpu = our_lib.clock_gettime_cpu
process_cpu_time = clock_gettime_cpu



# _last_switch_time = None

# timecount = Counter()
# funccount = Counter()

from trace import Trace

# def greenlet_trace(action, (origin, target)):
#     global _last_switch_time
#     then = _last_switch_time
#     now = _last_switch_time = process_cpu_time()

#     if then is not None:
#         blocking_time = now - then
#         if origin is not gevent.hub.get_hub():
#             timecount[origin] += blocking_time


t = Trace()

# def make_local_trace(func, parents):
#     start_time = timecount[gevent.getcurrent()]
#     def python_local_trace(frame, event, arg):
#         if event not in ('return', 'exception'):
#             return

#         execution_time = timecount[gevent.getcurrent()] - start_time + (process_cpu_time() - _last_switch_time)
#         funccount[func] += execution_time

#         for parent_func in parents:
#             funccount[parent_func] += execution_time
#         return python_local_trace

#     return python_local_trace

# func_start_time = {}

# def python_global_trace(frame, event, arg):
#     if event == 'call':
#         func = t.file_module_function_of(frame)
#         if func[0].startswith('/usr/lib'):  # or func[0].startswith('/home/serg/.virtualenvs/'):
#             return

#         f = frame
#         parents = []
#         while f.f_back:
#             parents.append(t.file_module_function_of(f.f_back))
#             f=f.f_back

#         return make_local_trace(func, parents)
#     elif event == 'c_call':
#         s = arg.__self__
#         fn = '{0}.{1}'.format(type(s).__name__, arg.__name__) if s is not None else arg.__name__ 
#         func_start_time[(fn, id(arg))] = timecount[gevent.getcurrent()]
#     elif event == 'c_return':
#         s = arg.__self__
#         fn = '{0}.{1}'.format(type(s).__name__, arg.__name__) if s is not None else arg.__name__ 
#         execution_time = timecount[gevent.getcurrent()] - func_start_time.pop((fn, id(arg)))
#         print fn, execution_time
#         funccount[fn] += execution_time



per_greenlet_stack = defaultdict(list)
cum_times = Counter()
own_times = Counter()
n_calls = Counter()


def greenlet_trace(action, (origin, target)):
    global _last_switch_time

    gevent_hub = gevent.hub.get_hub()
    # then = _last_switch_time
    # now = _last_switch_time = process_cpu_time()

    # if then is not None:
    #     blocking_time = now - then
    #     if origin is not gevent.hub.get_hub():
    #         timecount[origin] += blocking_time
    if origin is not gevent_hub:
        # walk over functions in origin stack and record their execution time
        now = process_cpu_time()
        for func_trace in per_greenlet_stack[origin]:
            func_trace.record_cum(now)

        if per_greenlet_stack[origin]:
            per_greenlet_stack[origin][-1].record_own(now)

    if target is not gevent_hub:
        # walk over functions in target stack and record their start time
        now = process_cpu_time()
        for func_trace in per_greenlet_stack[target]:
            func_trace.start_time = now


class FuncTrace(object):
    def __init__(self, func, start_time):
        self.func = func
        self.start_time = start_time

    def record_cum(self, now):
        cum_times[self.func] += now - self.start_time

    def record_own(self, now):
        own_times[self.func] += now - self.start_time


def push_stack(func):
    stack = per_greenlet_stack[gevent.getcurrent()]
    stack.append(FuncTrace(func, process_cpu_time()))


def pop_stack(func):
    stack = per_greenlet_stack[gevent.getcurrent()]
    if not stack:
        return
    func_trace = stack.pop()
    assert func_trace.func == func, '{0!r} != {1!r}'.format(func_trace.func, func)
    
    # record execution time as now - function start time
    func_trace.record_own(process_cpu_time())
    func_trace.record_cum(process_cpu_time()) 


def format_c_func(func):
    s = func.__self__
    return '{0}.{1}'.format(type(s).__name__, func.__name__) if s is not None else func.__name__ 


def python_global_trace(frame, event, arg):
    func = t.file_module_function_of(frame)

    #print event, func, arg
    if event == 'call':
        push_stack(func)

    elif event == 'return':
        pop_stack(func)

    elif event == 'c_call':
        push_stack(format_c_func(arg))

    elif event == 'c_return':
        pop_stack(format_c_func(arg))
    elif event == 'c_exception':
        pop_stack(format_c_func(arg))
    # if event == 'call':
    #     func = t.file_module_function_of(frame)
    #     if func[0].startswith('/usr/lib'):  # or func[0].startswith('/home/serg/.virtualenvs/'):
    #         return

    #     f = frame
    #     parents = []
    #     while f.f_back:
    #         parents.append(t.file_module_function_of(f.f_back))
    #         f=f.f_back

    #     return make_local_trace(func, parents)
    # elif event == 'c_call':
    #     s = arg.__self__
    #     fn = '{0}.{1}'.format(type(s).__name__, arg.__name__) if s is not None else arg.__name__ 
    #     func_start_time[(fn, id(arg))] = timecount[gevent.getcurrent()]
    # elif event == 'c_return':
    #     s = arg.__self__
    #     fn = '{0}.{1}'.format(type(s).__name__, arg.__name__) if s is not None else arg.__name__ 
    #     execution_time = timecount[gevent.getcurrent()] - func_start_time.pop((fn, id(arg)))
    #     print fn, execution_time
    #     funccount[fn] += execution_time


def start():
    greenlet.settrace(greenlet_trace)
    sys.setprofile(python_global_trace)


def finish():
    greenlet.settrace(None)
    sys.setprofile(None)


    # print "Top 10 greenlets by CPU usage:"
    # for g, total_time in timecount.most_common(10):
    #     print "\t{0!r}\t\t{1}".format(g, total_time)

    print "Top functions by CPU usage:"
    for func, total_time in cum_times.most_common(100):
        print "\t{0!r}\t\t{1}\t{2}".format(func, total_time, own_times[func])
