from floraconcierge.shortcuts import get_apiclient


def get_cities_list(
        country_id=None,
        region_id=None,
        limit=None,
        offset=None,
        with_not_delivered=None):
    return get_apiclient().services.geo.get_cities_list(
        country_id=country_id,
        region_id=region_id,
        limit=limit,
        offset=offset,
        with_not_delivered=with_not_delivered)


def get_city_by_id(id, with_not_delivered=None):
    return get_apiclient().services.geo.get_city_by_id(
        id,
        with_not_delivered=with_not_delivered)


def get_continent_by_id(id):
    return get_apiclient().services.geo.get_continent_by_id(id)


def get_continents_list(limit=None, offset=None):
    return get_apiclient().services.geo.get_continents_list(
        limit=limit,
        offset=offset)


def get_countries_list(parent_id=None, limit=None, offset=None):
    return get_apiclient().services.geo.get_countries_list(
        parent_id=parent_id,
        limit=limit,
        offset=offset)


def get_country_by_id(id):
    return get_apiclient().services.geo.get_country_by_id(id)


def get_region_by_id(id):
    return get_apiclient().services.geo.get_region_by_id(id)


def get_regions_list(country_id=None, limit=None, offset=None):
    return get_apiclient().services.geo.get_regions_list(
        country_id=country_id,
        limit=limit,
        offset=offset)


def get_sub_continent_by_id(id):
    return get_apiclient().services.geo.get_sub_continent_by_id(id)


def get_subcontinents_list(parent_id, limit=None, offset=None):
    return get_apiclient().services.geo.get_subcontinents_list(
        parent_id,
        limit=limit,
        offset=offset)


def get_user_ip_info():
    return get_apiclient().services.geo.get_user_ip_info()
