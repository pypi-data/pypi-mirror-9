class SourceMessage(dict):
    def __init__(self, data, source=None, key=None):
        self.source = source
        self.key = key
        dict.__init__(self, data)