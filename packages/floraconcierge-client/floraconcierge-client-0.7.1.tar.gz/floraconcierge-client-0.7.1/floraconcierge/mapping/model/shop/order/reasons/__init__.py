from floraconcierge.client.types import Object


class Text(Object):

    """
    :type id: int
    :type parent_id: int
    """

    def __init__(self, *args, **kwargs):
        self.id = None
        self.parent_id = None
        self.text = None
        self.title = None

        super(Text, self).__init__(*args, **kwargs)
