from floraconcierge.shortcuts import get_apiclient


def history_all_ref_codes(after_id=None):
    return get_apiclient().services.partner.history_all_ref_codes(
        after_id=after_id)


def check_ref_code(code):
    return get_apiclient().services.partner.check_ref_code(code)


def generate_ref_code():
    return get_apiclient().services.partner.generate_ref_code()


def history_ref_code(code, limit=None, offset=None):
    return get_apiclient().services.partner.history_ref_code(
        code,
        limit=limit,
        offset=offset)
