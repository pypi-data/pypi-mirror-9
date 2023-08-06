from floraconcierge.shortcuts import get_apiclient


def search(phone):
    return get_apiclient().services.phone.search(phone)
