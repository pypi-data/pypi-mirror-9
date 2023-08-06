class SourceMessage(dict):
    def __init__(self, data, source=None, key=None):
        self.source = source
        self.key = key
        dict.__init__(self, data)

    def __repr__(self):
        return 'SourceMessage({0}, {1!r}, {2!r})'.format(dict.__repr__(self), self.source, self.key)