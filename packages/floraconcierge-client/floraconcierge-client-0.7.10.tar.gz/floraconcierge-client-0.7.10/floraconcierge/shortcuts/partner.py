from floraconcierge.shortcuts import get_apiclient


def clients(partner_id=None, from=None, to=None):
    return get_apiclient().services.partner.clients(partner_id=partner_id, from=from, to=to)


def partner(id, from=None, to=None):
    return get_apiclient().services.partner.partner(id, from=from, to=to)


def partners():
    return get_apiclient().services.partner.partners()
