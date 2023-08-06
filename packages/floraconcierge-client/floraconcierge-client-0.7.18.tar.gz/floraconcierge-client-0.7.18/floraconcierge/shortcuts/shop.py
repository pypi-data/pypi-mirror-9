from floraconcierge.shortcuts import get_apiclient


def get_categories_list(parent_id=None):
    return get_apiclient().services.shop.get_categories_list(
        parent_id=parent_id)


def get_category_by_id(id):
    return get_apiclient().services.shop.get_category_by_id(id)


def get_currencies_list(order_id=None):
    return get_apiclient().services.shop.get_currencies_list(order_id=order_id)


def get_currency_by_id(id, order_id=None):
    return get_apiclient().services.shop.get_currency_by_id(
        id,
        order_id=order_id)


def get_gallery():
    return get_apiclient().services.shop.get_gallery()


def calculate_order(postObject):
    return get_apiclient().services.shop.calculate_order(postObject)


def get_order_by_id(id):
    return get_apiclient().services.shop.get_order_by_id(id)


def get_last_delivered():
    return get_apiclient().services.shop.get_last_delivered()


def get_user_orders(is_draft=None):
    return get_apiclient().services.shop.get_user_orders(is_draft=is_draft)


def get_order_reasons_text_by_id(id):
    return get_apiclient().services.shop.get_order_reasons_text_by_id(id)


def get_order_reasons_texts(parent_id=None):
    return get_apiclient().services.shop.get_order_reasons_texts(
        parent_id=parent_id)


def get_order_reason_by_id(id):
    return get_apiclient().services.shop.get_order_reason_by_id(id)


def get_order_reasons():
    return get_apiclient().services.shop.get_order_reasons()


def get_order_status(id):
    return get_apiclient().services.shop.get_order_status(id)


def submit_order_phone(postObject):
    return get_apiclient().services.shop.submit_order_phone(postObject)


def submit_order_request(postObject):
    return get_apiclient().services.shop.submit_order_request(postObject)


def submit_order(postObject):
    return get_apiclient().services.shop.submit_order(postObject)


def submit_order_ticket(id, key, message):
    return get_apiclient().services.shop.submit_order_ticket(id, key, message)


def get_order_tickets(id, key):
    return get_apiclient().services.shop.get_order_tickets(id, key)


def get_payment_system_by_id(id):
    return get_apiclient().services.shop.get_payment_system_by_id(id)


def get_payment_systems_list():
    return get_apiclient().services.shop.get_payment_systems_list()


def get_product_by_id(id):
    return get_apiclient().services.shop.get_product_by_id(id)


def get_products_of_day():
    return get_apiclient().services.shop.get_products_of_day()


def get_featured_products(city_id=None, country_id=None, product_of_day=None):
    return get_apiclient().services.shop.get_featured_products(
        city_id=city_id,
        country_id=country_id,
        product_of_day=product_of_day)


def lookup_products(postObject):
    return get_apiclient().services.shop.lookup_products(postObject)


def get_parent_product_by_id(id):
    return get_apiclient().services.shop.get_parent_product_by_id(id)


def search_products(query):
    return get_apiclient().services.shop.search_products(query)


def get_products_list(
        category=None,
        products=None,
        ingredient=None,
        random=None):
    return get_apiclient().services.shop.get_products_list(
        category=category,
        products=products,
        ingredient=ingredient,
        random=random)


def check_promo_code(code):
    return get_apiclient().services.shop.check_promo_code(code)


def get_review_by_id(id):
    return get_apiclient().services.shop.get_review_by_id(id)


def get_reviews_random(count=None):
    return get_apiclient().services.shop.get_reviews_random(count=count)


def submit_review(postObject):
    return get_apiclient().services.shop.submit_review(postObject)


def get_reviews_totals():
    return get_apiclient().services.shop.get_reviews_totals()


def get_reviews(
        limit=None,
        offset=None,
        product_id=None,
        after_id=None,
        before_id=None,
        city_id=None,
        category=None):
    return get_apiclient().services.shop.get_reviews(
        limit=limit,
        offset=offset,
        product_id=product_id,
        after_id=after_id,
        before_id=before_id,
        city_id=city_id,
        category=category)


def get_cash_salons_cities(country_id):
    return get_apiclient().services.shop.get_cash_salons_cities(country_id)


def get_cash_salons_countries():
    return get_apiclient().services.shop.get_cash_salons_countries()


def get_cash_salons_by_id(salon_id):
    return get_apiclient().services.shop.get_cash_salons_by_id(salon_id)


def get_cash_salons_by_city(city_id):
    return get_apiclient().services.shop.get_cash_salons_by_city(city_id)
