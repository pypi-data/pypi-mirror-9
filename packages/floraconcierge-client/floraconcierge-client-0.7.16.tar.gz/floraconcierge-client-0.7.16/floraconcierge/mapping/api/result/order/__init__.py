from floraconcierge.client.types import Object


class Submit(Object):
    """
    :type order: Object
    :type validation: Result
    """

    def __init__(self, *args, **kwargs):
        self.order = None
        self.validation = None

        super(Submit, self).__init__(*args, **kwargs)
