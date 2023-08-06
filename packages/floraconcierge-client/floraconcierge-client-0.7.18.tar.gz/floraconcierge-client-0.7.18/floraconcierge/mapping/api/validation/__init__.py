from floraconcierge.client.types import Object


class Result(Object):
    """
    :type errors: Object
    :type validated: Object
    """

    def __init__(self, *args, **kwargs):
        self.errors = None
        self.validated = None

        super(Result, self).__init__(*args, **kwargs)

    @property
    def is_valid(self):
        return not self.errors

    def __iter__(self):
        return iter(self.errors)
