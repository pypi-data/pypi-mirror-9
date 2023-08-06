from floraconcierge.shortcuts import get_apiclient


def email(email):
    return get_apiclient().services.discount.email(email)
