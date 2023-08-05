from floraconcierge.shortcuts import get_apiclient


def get_invoice_by_key(id):
    return get_apiclient().services.invoices.get_invoice_by_key(id)


def get_order_by_key(id):
    return get_apiclient().services.invoices.get_order_by_key(id)


def process_invoice_by_id(id, paysystem_id, amount, postObject):
    return get_apiclient().services.invoices.process_invoice_by_id(
        id,
        paysystem_id,
        amount,
        postObject)
