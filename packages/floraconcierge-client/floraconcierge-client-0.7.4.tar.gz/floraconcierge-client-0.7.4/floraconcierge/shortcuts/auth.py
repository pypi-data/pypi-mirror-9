from floraconcierge.shortcuts import get_apiclient


def set_result(token_id, is_success, data):
    return get_apiclient().services.auth.set_result(token_id, is_success, data)


def get_token(id):
    return get_apiclient().services.auth.get_token(id)
