"""Utilities to simplify Pymza task testing"""

import types
from pymza.message import SourceMessage


class FakeState(dict):
    """FakeState simulates task state using dict."""
    def __len__(self):
        raise RuntimeError('Calculating length of state is not supported')

    def range(self, key_from=None, key_to=None, include_value=True, reverse=False):

        left = lambda k: (True if key_from is None else key_from <= k)
        right = lambda k: (True if key_to is None else k <= key_to)

        keys = (k for k in sorted(self.keys()) if left(k) and right(k))
        if reverse:
            keys = reversed(list(keys))

        if include_value:
            return ((k, self[k]) for k in keys)
        else:
            return keys

    @property
    def _len(self):
        """Used for test assertion"""
        return dict.__len__(self)


class MessageList(list):
    def filter(self, message_type):
        return [x for x in self if x[0] == message_type]


class TestContainer(object):
    def __init__(self, task, config={}):
        self.task = task
        self.reset_state()
        self.init(config)

    def reset_state(self):
        self.state = FakeState()

    def init(self, config):
        if hasattr(self.task, 'init'):
            self.task.init(config)

    def process(self, message, source=None, key=None):
        result = self.task.process(SourceMessage(message, source=source, key=key), self.state)
        return _linearize_result(result)

    def window(self):
        result = self.task.window(self.state)
        return _linearize_result(result)


def _linearize_result(result):
    if result is None:
        return []

    if not isinstance(result, types.GeneratorType):
        result = [result]

    return MessageList([x for x in result if x is not None])
