from floraconcierge.shortcuts import get_apiclient


def address_delete(id):
    return get_apiclient().services.users.address_delete(id)


def address_list():
    return get_apiclient().services.users.address_list()


def address_process(postObject):
    return get_apiclient().services.users.address_process(postObject)


def calendar_delete(id):
    return get_apiclient().services.users.calendar_delete(id)


def calendar_list():
    return get_apiclient().services.users.calendar_list()


def calendar_process(postObject):
    return get_apiclient().services.users.calendar_process(postObject)


def check_password(email, password):
    return get_apiclient().services.users.check_password(email, password)


def exists(email):
    return get_apiclient().services.users.exists(email)


def get_logged_user(info=None):
    return get_apiclient().services.users.get_logged_user(info=info)


def login(email, password=None, remember=None, checkip=None):
    return get_apiclient().services.users.login(
        email,
        password=password,
        remember=remember,
        checkip=checkip)


def logout():
    return get_apiclient().services.users.logout()


def registration(email):
    return get_apiclient().services.users.registration(email)


def reset_password(email):
    return get_apiclient().services.users.reset_password(email)


def social_list():
    return get_apiclient().services.users.social_list()


def social_login(token):
    return get_apiclient().services.users.social_login(token)


def social_related():
    return get_apiclient().services.users.social_related()


def social_signin(service, redirect_success, redirect_fail):
    return get_apiclient().services.users.social_signin(
        service,
        redirect_success,
        redirect_fail)


def update_info(
        password=None,
        name=None,
        phone=None,
        country=None,
        city=None,
        birthday=None,
        flowers=None,
        feed_news=None,
        gender=None):
    return get_apiclient().services.users.update_info(
        password=password,
        name=name,
        phone=phone,
        country=country,
        city=city,
        birthday=birthday,
        flowers=flowers,
        feed_news=feed_news,
        gender=gender)
