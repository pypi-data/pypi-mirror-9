
class OffsetTracker(object):
    def __init__(self, offsets):
        self._offsets = offsets.copy()
        self._new_offsets = self._offsets.copy()
        self.is_modified = False

    def get(self, topic):
        return self._offsets.get(topic, 0)

    def set(self, topic, offset):
        self._new_offsets[topic] = offset

    def force_set(self, topic, offset):
        if not self.is_modified:
            self.is_modified = self._offsets.get(topic) != offset
        self._offsets[topic] = offset
        self._new_offsets[topic] = offset

    def __iter__(self):
        return iter(self._offsets.items())

    def apply_new_offsets(self):
        self.is_modified = self._offsets != self._new_offsets
        self._offsets = self._new_offsets.copy()

    def reset_is_modified(self):
        self.is_modified = False