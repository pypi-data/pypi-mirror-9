from floraconcierge.shortcuts import get_apiclient


def validate_order(postObject):
    return get_apiclient().services.validation.validate_order(postObject)
