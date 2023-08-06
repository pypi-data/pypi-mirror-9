class ValueObject(object):

    def __eq__(self, other):
        return self._attrs == other._attrs

    def __getattr__(self, name):
        return self._attrs[name]

    def __hash__(self):
        return hash(frozenset(self._attrs.items()))

    def __ne__(self, other):
        return not self.__eq__(other)
