from ordered_set import OrderedSet


class LimitedOrderedSet(OrderedSet):
    def __init__(self, limit=0, seq=()):
        setattr(self, 'limit', limit)

        super(LimitedOrderedSet, self).__init__(seq)

        self._check_length()

    def copy(self):
        return LimitedOrderedSet(limit=self.limit, seq=self)

    def discard(self, key):
        self.items.remove(key)
        self.map.pop(key)

    def _check_length(self):
        if not self.limit:
            return

        if len(self) > self.limit:
            for v in self[0:-self.limit]:
                self.remove(v)

    def __getitem__(self, item):
        res = super(LimitedOrderedSet, self).__getitem__(item)

        if isinstance(res, OrderedSet):
            return LimitedOrderedSet(self.limit, list(res))
        else:
            return res

    def __getstate__(self):
        return (self.limit, list(self))

    def __setstate__(self, state):
        self.__init__(*state)

    def add(self, key):
        result = super(LimitedOrderedSet, self).add(key)

        self._check_length()

        return result

    append = add
