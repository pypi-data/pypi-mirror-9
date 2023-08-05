from floraconcierge.shortcuts import get_apiclient


def get_watermark(img_name):
    return get_apiclient().services.img.get_watermark(img_name)
