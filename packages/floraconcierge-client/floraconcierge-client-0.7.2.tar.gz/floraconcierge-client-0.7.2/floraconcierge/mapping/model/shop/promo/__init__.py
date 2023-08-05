from floraconcierge.client.types import Object


class Code(Object):

    """
    :type code: str
    :type id: int
    """

    def __init__(self, *args, **kwargs):
        self.code = None
        self.discount = None
        self.id = None

        super(Code, self).__init__(*args, **kwargs)
