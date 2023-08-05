from floraconcierge.client.types import Object


class Invoice(Object):

    """
    :type id: int
    :type paid: int
    """

    def __init__(self, *args, **kwargs):
        self.cost = None
        self.created = None
        self.id = None
        self.is_hold = None
        self.is_paid = None
        self.is_test = None
        self.key = None
        self.order_id = None
        self.paid = None
        self.paysystem_id = None
        self.price = None
        self.url = None

        super(Invoice, self).__init__(*args, **kwargs)


class Reason(Object):

    """
    :type id: int
    :type name: str
    """

    def __init__(self, *args, **kwargs):
        self.id = None
        self.name = None

        super(Reason, self).__init__(*args, **kwargs)
