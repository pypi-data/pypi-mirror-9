from floraconcierge.client.types import Object


class Collection(Object, list):
    def __init__(self, *args, **kwargs):
        super(Collection, self).__init__(*args, **kwargs)

        self.extend(self.items)

    def find(self, **kwargs):
        _matches = len(kwargs)

        for k, v in kwargs.iteritems():
            kwargs[k] = unicode(v).lower()

        for item in self:
            found = 0
            for k, v in kwargs.iteritems():
                if unicode(getattr(item, k)).lower() == v:
                    found += 1

            if found == _matches:
                return item

        return None

    def findall(self, **kwargs):
        _matches = len(kwargs)

        for k, v in kwargs.iteritems():
            kwargs[k] = unicode(v).lower()

        items = []
        for item in self:
            found = 0
            for k, v in kwargs.iteritems():
                if unicode(getattr(item, k)).lower() == v:
                    found += 1

            if found == _matches:
                items.append(item)

        from floraconcierge.mapping import Collection as CollectionObj

        return CollectionObj({
            'count': len(items),
            'items': items,
            'offset': 0,
            'total': len(items)
        })
