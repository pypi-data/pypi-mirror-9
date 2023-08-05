import math

from floraconcierge.client.types import Object


DEFAULT_PRODUCT_IMAGES_LIST = {
    'default': 'https://www.florastatic.net/img/products/%s_250.jpg',
    'small': 'https://www.florastatic.net/img/products/%s_100.jpg',
    'middle': 'https://www.florastatic.net/img/products/%s_250.jpg',
    'big': 'https://www.florastatic.net/img/products/%s_500.jpg',
    'thumb_100': 'https://www.florastatic.net/img/products/%s_100.jpg',
    'thumb_250': 'https://www.florastatic.net/img/products/%s_250.jpg',
    'thumb_500': 'https://www.florastatic.net/img/products/%s_500.jpg',
}
_product_images_urls = None


def get_product_images_urls():
    global _product_images_urls

    if not _product_images_urls:
        from django.conf import settings
        from django.core.exceptions import ImproperlyConfigured

        try:
            urls = getattr(settings, 'FLORACONCIERGE_PRODUCT_IMAGES', DEFAULT_PRODUCT_IMAGES_LIST)
        except ImproperlyConfigured:
            urls = DEFAULT_PRODUCT_IMAGES_LIST

        if not isinstance(urls, dict):
            raise ImproperlyConfigured('FLORACONCIERGE_PRODUCT_IMAGES configuration must be dict')

        _product_images_urls = urls

    return _product_images_urls


class Currency(Object):
    def __init__(self, *args, **kwargs):
        super(Currency, self).__init__(*args, **kwargs)

        try:
            self.rounding = float(self.rounding)
        except (ValueError, TypeError):
            self.rounding = .0

    def round(self, value, decimals=0):
        if not self.rounding:
            multiplier = float(10 ** decimals)

            return int(value * multiplier) / multiplier
        else:
            if self.rounding_direction == 'desc':
                return int(self.rounding * math.ceil(value / self.rounding))
            else:
                return int(self.rounding * math.floor(value / self.rounding))

    def _format(self, value):
        return self.format % value

    def convert(self, value):
        return self._format(self.convert_float(value))

    def convert_float(self, value):
        return self.round(float(self.usdvalue) * float(value), 2)


class Product(Object):
    def __init__(self, *args, **kwargs):
        super(Product, self).__init__(*args, **kwargs)

        urls = {}
        if self.url:
            for k, v in get_product_images_urls().iteritems():
                urls[k] = v % self.id

        self.urls = urls
