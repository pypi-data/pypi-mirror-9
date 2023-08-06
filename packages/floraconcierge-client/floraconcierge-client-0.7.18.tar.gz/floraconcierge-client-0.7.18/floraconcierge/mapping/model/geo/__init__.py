from floraconcierge.client.types import Object


class Subcontinent(Object):

    """
    :type id: int
    :type iso: str
    :type name: str
    :type price: int
    :type slug: str
    """

    def __init__(self, *args, **kwargs):
        self.continent_id = None
        self.id = None
        self.iso = None
        self.name = None
        self.price = None
        self.slug = None

        super(Subcontinent, self).__init__(*args, **kwargs)


class Continent(Object):

    """
    :type id: int
    :type iso: str
    :type name: str
    :type slug: str
    """

    def __init__(self, *args, **kwargs):
        self.id = None
        self.iso = None
        self.name = None
        self.slug = None

        super(Continent, self).__init__(*args, **kwargs)


class City(Object):

    """
    :type id: int
    :type name: str
    :type slug: str
    """

    def __init__(self, *args, **kwargs):
        self.country_id = None
        self.deliver = None
        self.gmt = None
        self.id = None
        self.large = None
        self.lat = None
        self.lng = None
        self.name = None
        self.name_original = None
        self.region_id = None
        self.slug = None
        self.timezone = None
        self.title_unique = None

        super(City, self).__init__(*args, **kwargs)


class Country(Object):

    """
    :type id: int
    :type iso: str
    :type name: str
    :type slug: str
    """

    def __init__(self, *args, **kwargs):
        self.fips = None
        self.id = None
        self.is_cis = None
        self.iso = None
        self.name = None
        self.populations = None
        self.slug = None
        self.subcontinent_id = None
        self.work = None

        super(Country, self).__init__(*args, **kwargs)


class Region(Object):

    """
    :type id: int
    :type iso: str
    :type name: str
    :type slug: str
    """

    def __init__(self, *args, **kwargs):
        self.country_id = None
        self.fips = None
        self.id = None
        self.iso = None
        self.name = None
        self.name_origin = None
        self.populations = None
        self.slug = None

        super(Region, self).__init__(*args, **kwargs)
