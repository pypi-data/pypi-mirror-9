from floraconcierge.client.types import Object
from floraconcierge.mapping.mixins.model.shop import Currency as CurrencyMixin
from floraconcierge.mapping.mixins.model.shop import Product as ProductMixin


class Order(Object):

    """
    :type id: int
    :type invoices: list of Invoice|Collection
    :type is_sms: str
    :type products: list of Child|Collection
    :type user: User
    """

    def __init__(self, *args, **kwargs):
        self.app_id = None
        self.currency_id = None
        self.date_delive = None
        self.date_order = None
        self.discount = None
        self.id = None
        self.invoices = None
        self.is_sms = None
        self.language = None
        self.order_key = None
        self.other = None
        self.photo = None
        self.products = None
        self.products_free = None
        self.promocode = None
        self.reason = None
        self.receiver_address = None
        self.receiver_city = None
        self.receiver_city_id = None
        self.receiver_country = None
        self.receiver_country_id = None
        self.receiver_email = None
        self.receiver_name = None
        self.receiver_phone = None
        self.sender_city = None
        self.sender_country = None
        self.sender_email = None
        self.sender_gmt = None
        self.sender_ip = None
        self.sender_name = None
        self.sender_phone = None
        self.status = None
        self.status_changed = None
        self.status_plain = None
        self.summ = None
        self.summ_manual = None
        self.time = None
        self.total = None
        self.totals = None
        self.totalusd = None
        self.type = None
        self.user = None
        self.user_id = None
        self.wishes = None

        super(Order, self).__init__(*args, **kwargs)


class Currency(CurrencyMixin):

    """
    :type id: int
    :type name: str
    """

    def __init__(self, *args, **kwargs):
        self.description = None
        self.format = None
        self.id = None
        self.name = None
        self.rounding = None
        self.rounding_direction = None
        self.title = None
        self.usdvalue = None

        super(Currency, self).__init__(*args, **kwargs)


class Paysystem(Object):

    """
    :type id: int
    :type name: str
    :type slug: str
    """

    def __init__(self, *args, **kwargs):
        self.id = None
        self.imageurl = None
        self.name = None
        self.order = None
        self.slug = None
        self.text = None

        super(Paysystem, self).__init__(*args, **kwargs)


class Salon(Object):

    """
    :type id: int
    :type name: str
    :type type: str
    """

    def __init__(self, *args, **kwargs):
        self.address = None
        self.address_link = None
        self.city_id = None
        self.contacts = None
        self.cost = None
        self.cost_usd = None
        self.florist_id = None
        self.id = None
        self.name = None
        self.type = None

        super(Salon, self).__init__(*args, **kwargs)


class Product(ProductMixin):

    """
    :type categories: list|Collection
    :type children: list of Child|Collection
    :type complex: bool
    :type id: int
    :type price_text: str
    :type properties: str
    :type slug: str
    :type weight: int
    """

    def __init__(self, *args, **kwargs):
        self.available = None
        self.categories = None
        self.children = None
        self.comment = None
        self.complex = None
        self.composition = None
        self.compositions_info = None
        self.description = None
        self.gallery = None
        self.id = None
        self.order = None
        self.price = None
        self.price_text = None
        self.prices = None
        self.priceusd = None
        self.properties = None
        self.realprice = None
        self.realprices = None
        self.realpriceusd = None
        self.search_tags = None
        self.slug = None
        self.title = None
        self.type = None
        self.url = None
        self.weight = None

        super(Product, self).__init__(*args, **kwargs)
