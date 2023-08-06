from floraconcierge.shortcuts import get_apiclient


def clients(partner_id=None, from_datetime=None, to_datetime=None):
    return get_apiclient().services.partner.clients(
        partner_id=partner_id,
        from_datetime=from_datetime,
        to_datetime=to_datetime)


def partner(id, from_datetime=None, to_datetime=None):
    return get_apiclient().services.partner.partner(
        id,
        from_datetime=from_datetime,
        to_datetime=to_datetime)


def partners():
    return get_apiclient().services.partner.partners()
