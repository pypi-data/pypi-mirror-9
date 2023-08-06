from floraconcierge.shortcuts import get_apiclient


def clients(partner_id=None, from1=None, to=None):
    return get_apiclient().services.partner.clients(partner_id=partner_id, from1=from1, to=to)


def partner(id, from1=None, to=None):
    return get_apiclient().services.partner.partner(id, from1=from1, to=to)


def partners():
    return get_apiclient().services.partner.partners()
