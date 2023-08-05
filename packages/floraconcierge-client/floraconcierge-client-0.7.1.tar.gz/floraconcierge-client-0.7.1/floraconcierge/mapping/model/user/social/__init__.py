from floraconcierge.client.types import Object


class Signin(Object):

    """
    :type id: int
    """

    def __init__(self, *args, **kwargs):
        self.app_id = None
        self.data = None
        self.expire = None
        self.id = None
        self.is_success = None
        self.redirect_fail = None
        self.redirect_success = None
        self.service = None
        self.token = None
        self.user_id = None

        super(Signin, self).__init__(*args, **kwargs)
