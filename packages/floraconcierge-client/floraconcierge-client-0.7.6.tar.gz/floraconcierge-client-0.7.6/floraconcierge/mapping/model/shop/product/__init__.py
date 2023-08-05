from floraconcierge.client.types import Object


class Child(Object):

    """
    """

    def __init__(self, *args, **kwargs):
        self.count = None
        self.product = None

        super(Child, self).__init__(*args, **kwargs)


class Color(Object):

    """
    :type id: int
    """

    def __init__(self, *args, **kwargs):
        self.id = None
        self.title = None

        super(Color, self).__init__(*args, **kwargs)


class Category(Object):

    """
    :type id: int
    :type name: str
    :type parent_id: int
    :type slug: str
    """

    def __init__(self, *args, **kwargs):
        self.id = None
        self.is_hand_order = None
        self.name = None
        self.parent_id = None
        self.slug = None
        self.type = None
        self.weight = None

        super(Category, self).__init__(*args, **kwargs)
