"""Utilities to simplify Pymza task testing"""


class FakeState(dict):
    """FakeState simulates task state using dict."""
    def __len__(self):
        raise RuntimeError('Calculating length of state is not supported')

    def range(self, key_from=None, key_to=None, *args, **kwargs):

        left = lambda k: (True if key_from is None else key_from <= k)
        right = lambda k: (True if key_to is None else k <= key_to)

        return [(k, v) for k, v in self.items() if left(k) and right(k)]

    @property 
    def _len(self):
        """Used for test assertion"""
        return dict.__len__(self)