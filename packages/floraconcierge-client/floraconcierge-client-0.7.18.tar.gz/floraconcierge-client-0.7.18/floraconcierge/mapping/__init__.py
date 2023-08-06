from floraconcierge.mapping.mixins import Collection as CollectionMixin


class Collection(CollectionMixin):

    """
    :type items: list of Object
    """

    def __init__(self, *args, **kwargs):
        self.count = None
        self.items = None
        self.offset = None
        self.total = None

        super(Collection, self).__init__(*args, **kwargs)
