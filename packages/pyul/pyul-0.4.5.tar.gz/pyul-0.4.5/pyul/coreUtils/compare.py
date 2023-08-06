__all__ = ['ComparableMixin']


class ComparableMixin(object):

    def _compare(self, other, method):
        try:
            return method(self._cmpkey(), other._cmpkey())
        except (AttributeError, TypeError):
            return NotImplemented

    def _cmpkey(self):
        raise NotImplementedError('Please implement the _cmpkey method for your subclass!')

    def __lt__(self, other):
        return self._compare(other, lambda s, o: s < o)

    def __le__(self, other):
        return self._compare(other, lambda s, o: s <= o)

    def __ge__(self, other):
        return self._compare(other, lambda s, o: s >= o)

    def __gt__(self, other):
        return self._compare(other, lambda s, o: s > o)

    def __eq__(self, other):
        return self._compare(other, lambda s, o: s == o)

    def __ne__(self, other):
        return self._compare(other, lambda s, o: s != o)
