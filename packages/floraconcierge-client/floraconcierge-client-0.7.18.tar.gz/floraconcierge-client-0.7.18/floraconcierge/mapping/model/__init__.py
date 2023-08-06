from floraconcierge.client.types import Object


class Language(Object):

    """
    :type id: int
    :type iso: str
    :type name: str
    """

    def __init__(self, *args, **kwargs):
        self.icon = None
        self.id = None
        self.iso = None
        self.locale = None
        self.name = None

        super(Language, self).__init__(*args, **kwargs)


class Snippet(Object):

    """
    :type id: int
    """

    def __init__(self, *args, **kwargs):
        self.application_id = None
        self.content = None
        self.id = None
        self.uid = None

        super(Snippet, self).__init__(*args, **kwargs)


class User(Object):

    """
    :type auth: Auth
    :type gender: str
    :type id: int
    :type name: str
    """

    def __init__(self, *args, **kwargs):
        self.app_id = None
        self.auth = None
        self.birthday = None
        self.city = None
        self.country = None
        self.date_registration = None
        self.discount = None
        self.email = None
        self.feed_news = None
        self.feed_sms = None
        self.flowers = None
        self.gender = None
        self.id = None
        self.ip = None
        self.name = None
        self.phone = None
        self.phone_home = None
        self.phone_work = None
        self.timezone = None

        super(User, self).__init__(*args, **kwargs)


class Page(Object):

    """
    :type id: int
    :type slug: str
    """

    def __init__(self, *args, **kwargs):
        self.application_id = None
        self.category = None
        self.content = None
        self.date = None
        self.file_name = None
        self.id = None
        self.is_file = None
        self.order = None
        self.promo = None
        self.published = None
        self.slug = None
        self.title = None
        self.url = None

        super(Page, self).__init__(*args, **kwargs)


class Review(Object):

    """
    :type category: str
    :type gender: str
    :type id: int
    :type name: str
    """

    def __init__(self, *args, **kwargs):
        self.allow_partners = None
        self.answer = None
        self.app_id = None
        self.avatar_url = None
        self.category = None
        self.city = None
        self.city_id = None
        self.comment = None
        self.comment_courier = None
        self.comment_florist = None
        self.comment_florist_good = None
        self.comment_flowers_quality = None
        self.comment_flowers_rating = None
        self.comment_manager = None
        self.comment_operator = None
        self.created = None
        self.email = None
        self.external_url = None
        self.gender = None
        self.id = None
        self.name = None
        self.order_city = None
        self.order_date = None
        self.order_id = None
        self.phone = None
        self.product_id = None
        self.status = None
        self.urls = None

        super(Review, self).__init__(*args, **kwargs)
