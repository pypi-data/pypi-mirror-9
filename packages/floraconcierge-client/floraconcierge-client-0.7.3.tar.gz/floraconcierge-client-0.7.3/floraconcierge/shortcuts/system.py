from floraconcierge.shortcuts import get_apiclient


def send_feedback(postObject):
    return get_apiclient().services.system.send_feedback(postObject)


def get_language_by_id(id):
    return get_apiclient().services.system.get_language_by_id(id)


def get_languages_list(limit=None, offset=None):
    return get_apiclient().services.system.get_languages_list(
        limit=limit,
        offset=offset)


def get_page_by_id(id):
    return get_apiclient().services.system.get_page_by_id(id)


def get_pages_list(category=None):
    return get_apiclient().services.system.get_pages_list(category=category)


def get_snippet_by_id(id):
    return get_apiclient().services.system.get_snippet_by_id(id)
