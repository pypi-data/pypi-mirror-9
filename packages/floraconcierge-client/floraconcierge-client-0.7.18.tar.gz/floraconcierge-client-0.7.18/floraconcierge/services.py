from floraconcierge.client import Service
# noinspection PyShadowingBuiltins


class Shop(Service):

    def get_categories_list(self, parent_id=None):
        """
        :rtype : list of Category|Collection
        """
        return self._callapi("shop/categories", get={"parent_id": parent_id})

    def get_category_by_id(self, id):
        """
        :rtype : Category
        """
        return self._callapi("shop/category", get={"id": id})

    def get_currencies_list(self, order_id=None):
        """
        :rtype : list of Currency|Collection
        """
        return self._callapi("shop/currencies", get={"order_id": order_id})

    def get_currency_by_id(self, id, order_id=None):
        """
        :rtype : Currency
        """
        return self._callapi(
            "shop/currency",
            get={
                "id": id,
                "order_id": order_id})

    def get_gallery(self):
        """
        :rtype : Collection
        """
        return self._callapi("shop/gallery")

    def calculate_order(self, postObject):
        """
        :rtype : Order
        """
        return self._callapi("shop/order/calculate", post=postObject)

    def get_order_by_id(self, id):
        """
        :rtype : Order
        """
        return self._callapi("shop/order/get", get={"id": id})

    def get_last_delivered(self):
        """
        :rtype : Collection
        """
        return self._callapi("shop/order/lastdelivered")

    def get_user_orders(self, is_draft=None):
        """
        :rtype : list of Order|Collection
        """
        return self._callapi("shop/order/my", get={"is_draft": is_draft})

    def get_order_reasons_text_by_id(self, id):
        """
        :rtype : Text
        """
        return self._callapi("shop/order/reason/text", get={"id": id})

    def get_order_reasons_texts(self, parent_id=None):
        """
        :rtype : list of Text|Collection
        """
        return self._callapi(
            "shop/order/reason/texts",
            get={
                "parent_id": parent_id})

    def get_order_reason_by_id(self, id):
        """
        :rtype : Reason
        """
        return self._callapi("shop/order/reason", get={"id": id})

    def get_order_reasons(self):
        """
        :rtype : list of Reason|Collection
        """
        return self._callapi("shop/order/reasons")

    def get_order_status(self, id):
        """
        :rtype : list
        """
        return self._callapi("shop/order/status", get={"id": id})

    def submit_order_phone(self, postObject):
        """
        :rtype : Submit
        """
        return self._callapi("shop/order/submit/phone", post=postObject)

    def submit_order_request(self, postObject):
        """
        :rtype : int
        """
        return self._callapi("shop/order/submit/request", post=postObject)

    def submit_order(self, postObject):
        """
        :rtype : Submit
        """
        return self._callapi("shop/order/submit", post=postObject)

    def submit_order_ticket(self, id, key, message):
        """
        :rtype : bool
        """
        return self._callapi(
            "shop/order/tickets/submit",
            get={
                "id": id,
                "key": key,
                "message": message})

    def get_order_tickets(self, id, key):
        """
        :rtype : list of list|Collection
        """
        return self._callapi("shop/order/tickets", get={"id": id, "key": key})

    def get_payment_system_by_id(self, id):
        """
        :rtype : Paysystem
        """
        return self._callapi("shop/paysystem", get={"id": id})

    def get_payment_systems_list(self):
        """
        :rtype : Collection|list of Paysystem
        """
        return self._callapi("shop/paysystems")

    def get_product_by_id(self, id):
        """
        :rtype : Product
        """
        return self._callapi("shop/product", get={"id": id})

    def get_products_of_day(self):
        """
        :rtype : list of Product|Collection
        """
        return self._callapi("shop/products/day")

    def get_featured_products(
            self,
            city_id=None,
            country_id=None,
            product_of_day=None):
        """
        :rtype : list of Product|Collection
        """
        return self._callapi(
            "shop/products/featured",
            get={
                "city_id": city_id,
                "country_id": country_id,
                "product_of_day": product_of_day})

    def lookup_products(self, postObject):
        """
        :rtype : list of Product|Collection
        """
        return self._callapi("shop/products/lookup", post=postObject)

    def get_parent_product_by_id(self, id):
        """
        :rtype : Product
        """
        return self._callapi("shop/products/parent", get={"id": id})

    def search_products(self, query):
        """
        :rtype : list of Product|Collection
        """
        return self._callapi("shop/products/search", get={"query": query})

    def get_products_list(
            self,
            category=None,
            products=None,
            ingredient=None,
            random=None):
        """
        :rtype : list of Product|Collection
        """
        return self._callapi(
            "shop/products",
            get={
                "category": category,
                "products": products,
                "ingredient": ingredient,
                "random": random})

    def check_promo_code(self, code):
        """
        :rtype : Code
        """
        return self._callapi("shop/promo/check", get={"code": code})

    def get_review_by_id(self, id):
        """
        :rtype : Review
        """
        return self._callapi("shop/review", get={"id": id})

    def get_reviews_random(self, count=None):
        """
        :rtype : Collection|list of Review
        """
        return self._callapi("shop/reviews/random", get={"count": count})

    def submit_review(self, postObject):
        """
        :rtype : int
        """
        return self._callapi("shop/reviews/submit", post=postObject)

    def get_reviews_totals(self):
        """
        :rtype : Stdclass
        """
        return self._callapi("shop/reviews/total")

    def get_reviews(
            self,
            limit=None,
            offset=None,
            product_id=None,
            after_id=None,
            before_id=None,
            city_id=None,
            category=None):
        """
        :rtype : Collection|list of Review
        """
        return self._callapi(
            "shop/reviews",
            get={
                "limit": limit,
                "offset": offset,
                "product_id": product_id,
                "after_id": after_id,
                "before_id": before_id,
                "city_id": city_id,
                "category": category})

    def get_cash_salons_cities(self, country_id):
        """
        :rtype : City|Collection
        """
        return self._callapi(
            "shop/salons/cities",
            get={
                "country_id": country_id})

    def get_cash_salons_countries(self):
        """
        :rtype : Country
        """
        return self._callapi("shop/salons/countries")

    def get_cash_salons_by_id(self, salon_id):
        """
        :rtype : Salon
        """
        return self._callapi("shop/salons/salon", get={"salon_id": salon_id})

    def get_cash_salons_by_city(self, city_id):
        """
        :rtype : list of Salon|Collection
        """
        return self._callapi("shop/salons", get={"city_id": city_id})
# noinspection PyShadowingBuiltins


class Users(Service):

    def address_delete(self, id):
        """
        :rtype : int
        """
        return self._callapi("users/address/delete", get={"id": id})

    def address_list(self):
        """
        :rtype : list of Address|Collection
        """
        return self._callapi("users/address/list")

    def address_process(self, postObject):
        """
        :rtype : Address
        """
        return self._callapi("users/address/process", post=postObject)

    def calendar_delete(self, id):
        """
        :rtype : int
        """
        return self._callapi("users/calendar/delete", get={"id": id})

    def calendar_list(self):
        """
        :rtype : list of Calendar|Collection
        """
        return self._callapi("users/calendar/list")

    def calendar_process(self, postObject):
        """
        :rtype : Calendar
        """
        return self._callapi("users/calendar/process", post=postObject)

    def check_password(self, email, password):
        """
        :rtype : bool
        """
        return self._callapi(
            "users/checkpassword",
            get={
                "email": email,
                "password": password})

    def exists(self, email):
        """
        :rtype : bool
        """
        return self._callapi("users/exists", get={"email": email})

    def get_logged_user(self, info=None):
        """
        :rtype : Stdclass|Null|User
        """
        return self._callapi("users/logged", get={"info": info})

    def login(self, email, password=None, remember=None, checkip=None):
        """
        :rtype : User
        """
        return self._callapi(
            "users/login",
            get={
                "email": email,
                "password": password,
                "remember": remember,
                "checkip": checkip})

    def logout(self):
        """
        :rtype : bool
        """
        return self._callapi("users/logout")

    def registration(self, email):
        """
        :rtype : bool
        """
        return self._callapi("users/registration", get={"email": email})

    def reset_password(self, email):
        """
        :rtype : User
        """
        return self._callapi("users/resetpassword", get={"email": email})

    def social_list(self):
        """
        :rtype : Stdclass
        """
        return self._callapi("users/social/list")

    def social_login(self, token):
        """
        :rtype : User
        """
        return self._callapi("users/social/login", get={"token": token})

    def social_related(self):
        """
        :rtype : Stdclass
        """
        return self._callapi("users/social/related")

    def social_signin(self, service, redirect_success, redirect_fail):
        """
        :rtype : str
        """
        return self._callapi(
            "users/social/signin",
            get={
                "service": service,
                "redirect_success": redirect_success,
                "redirect_fail": redirect_fail})

    def update_info(
            self,
            password=None,
            name=None,
            phone=None,
            country=None,
            city=None,
            birthday=None,
            flowers=None,
            feed_news=None,
            gender=None):
        """
        :rtype : User
        """
        return self._callapi(
            "users/update",
            get={
                "password": password,
                "name": name,
                "phone": phone,
                "country": country,
                "city": city,
                "birthday": birthday,
                "flowers": flowers,
                "feed_news": feed_news,
                "gender": gender})
# noinspection PyShadowingBuiltins


class Img(Service):

    def get_watermark(self, img_name):
        """
        :rtype : Stdclass
        """
        return self._callapi("img/watermark", get={"img_name": img_name})
# noinspection PyShadowingBuiltins


class Phone(Service):

    def search(self, phone):
        """
        :rtype : Stdclass
        """
        return self._callapi("phone/search", get={"phone": phone})
# noinspection PyShadowingBuiltins


class Invoices(Service):

    def get_invoice_by_key(self, id):
        """
        :rtype : Invoice
        """
        return self._callapi("invoices/invoice", get={"id": id})

    def get_order_by_key(self, id):
        """
        :rtype : Order
        """
        return self._callapi("invoices/order", get={"id": id})

    def process_invoice_by_id(self, id, paysystem_id, amount, postObject):
        """
        :rtype : bool
        """
        return self._callapi(
            "invoices/process",
            get={
                "id": id,
                "paysystem_id": paysystem_id,
                "amount": amount},
            post=postObject)
# noinspection PyShadowingBuiltins


class System(Service):

    def send_feedback(self, postObject):
        """
        :rtype : bool
        """
        return self._callapi("system/feedback", post=postObject)

    def get_language_by_id(self, id):
        """
        :rtype : Language
        """
        return self._callapi("system/language", get={"id": id})

    def get_languages_list(self, limit=None, offset=None):
        """
        :rtype : Collection|list of Language
        """
        return self._callapi(
            "system/languages",
            get={
                "limit": limit,
                "offset": offset})

    def get_page_by_id(self, id):
        """
        :rtype : Page
        """
        return self._callapi("system/page", get={"id": id})

    def get_pages_list(self, category=None):
        """
        :rtype : list of Page|Collection
        """
        return self._callapi("system/pages", get={"category": category})

    def get_snippet_by_id(self, id):
        """
        :rtype : Snippet
        """
        return self._callapi("system/snippet", get={"id": id})
# noinspection PyShadowingBuiltins


class Auth(Service):

    def set_result(self, token_id, is_success, data):
        """
        :rtype : Signin
        """
        return self._callapi(
            "auth/result",
            get={
                "token_id": token_id,
                "is_success": is_success,
                "data": data})

    def get_token(self, id):
        """
        :rtype : Signin
        """
        return self._callapi("auth/token", get={"id": id})
# noinspection PyShadowingBuiltins


class Discount(Service):

    def email(self, email):
        """
        :rtype : bool
        """
        return self._callapi("discount/email", get={"email": email})
# noinspection PyShadowingBuiltins


class Partner(Service):

    def clients(self, partner_id=None, from_datetime=None, to_datetime=None):
        """
        :rtype : list of Stdclass|list
        """
        return self._callapi(
            "partner/clients",
            get={
                "partner_id": partner_id,
                "from_datetime": from_datetime,
                "to_datetime": to_datetime})

    def partner(self, id, from_datetime=None, to_datetime=None):
        """
        :rtype : Stdclass
        """
        return self._callapi(
            "partner/partner",
            get={
                "id": id,
                "from_datetime": from_datetime,
                "to_datetime": to_datetime})

    def partners(self):
        """
        :rtype : list of Stdclass|list
        """
        return self._callapi("partner/partners")
# noinspection PyShadowingBuiltins


class Validation(Service):

    def validate_order(self, postObject):
        """
        :rtype : Result
        """
        return self._callapi("validation/order", post=postObject)
# noinspection PyShadowingBuiltins


class Geo(Service):

    def get_cities_list(
            self,
            country_id=None,
            region_id=None,
            limit=None,
            offset=None,
            with_not_delivered=None):
        """
        :rtype : list of City|Collection
        """
        return self._callapi(
            "geo/cities",
            get={
                "country_id": country_id,
                "region_id": region_id,
                "limit": limit,
                "offset": offset,
                "with_not_delivered": with_not_delivered})

    def get_city_by_id(self, id, with_not_delivered=None):
        """
        :rtype : City
        """
        return self._callapi(
            "geo/city",
            get={
                "id": id,
                "with_not_delivered": with_not_delivered})

    def get_continent_by_id(self, id):
        """
        :rtype : Continent
        """
        return self._callapi("geo/continent", get={"id": id})

    def get_continents_list(self, limit=None, offset=None):
        """
        :rtype : list of Continent|Collection
        """
        return self._callapi(
            "geo/continents",
            get={
                "limit": limit,
                "offset": offset})

    def get_countries_list(self, parent_id=None, limit=None, offset=None):
        """
        :rtype : list of Country|Collection
        """
        return self._callapi(
            "geo/countries",
            get={
                "parent_id": parent_id,
                "limit": limit,
                "offset": offset})

    def get_country_by_id(self, id):
        """
        :rtype : Country
        """
        return self._callapi("geo/country", get={"id": id})

    def get_region_by_id(self, id):
        """
        :rtype : Region
        """
        return self._callapi("geo/region", get={"id": id})

    def get_regions_list(self, country_id=None, limit=None, offset=None):
        """
        :rtype : list of Country|Collection
        """
        return self._callapi(
            "geo/regions",
            get={
                "country_id": country_id,
                "limit": limit,
                "offset": offset})

    def get_sub_continent_by_id(self, id):
        """
        :rtype : Subcontinent
        """
        return self._callapi("geo/subcontinent", get={"id": id})

    def get_subcontinents_list(self, parent_id, limit=None, offset=None):
        """
        :rtype : list of Subcontinent|Collection
        """
        return self._callapi(
            "geo/subcontinents",
            get={
                "parent_id": parent_id,
                "limit": limit,
                "offset": offset})

    def get_user_ip_info(self):
        """
        :rtype : Stdclass
        """
        return self._callapi("geo/useripinfo")


class Manager(object):

    def __init__(self, apiclient):
        self.shop = Shop(apiclient)
        self.users = Users(apiclient)
        self.img = Img(apiclient)
        self.phone = Phone(apiclient)
        self.invoices = Invoices(apiclient)
        self.system = System(apiclient)
        self.auth = Auth(apiclient)
        self.discount = Discount(apiclient)
        self.partner = Partner(apiclient)
        self.validation = Validation(apiclient)
        self.geo = Geo(apiclient)
