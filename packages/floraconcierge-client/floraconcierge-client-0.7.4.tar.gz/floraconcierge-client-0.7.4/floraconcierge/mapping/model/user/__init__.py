from floraconcierge.client.types import Object


class Auth(Object):

    """
    :type id: int
    """

    def __init__(self, *args, **kwargs):
        self.app_id = None
        self.auth_key = None
        self.checkip = None
        self.expire = None
        self.id = None
        self.ip = None
        self.lasttime = None
        self.remember = None
        self.user_id = None

        super(Auth, self).__init__(*args, **kwargs)


class Address(Object):

    """
    :type id: int
    :type name: str
    """

    def __init__(self, *args, **kwargs):
        self.address = None
        self.city = None
        self.city_id = None
        self.country = None
        self.country_id = None
        self.email = None
        self.id = None
        self.name = None
        self.phone = None

        super(Address, self).__init__(*args, **kwargs)
