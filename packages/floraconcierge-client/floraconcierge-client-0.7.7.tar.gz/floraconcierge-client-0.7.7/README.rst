Version 0.7.7

FloraConcierge is worldwide flowers delivery service. We provide api services for
building your own flowers delivery e-commerce and submit users orders into our system.

All information at http://www.floraexpress.ru/

You can simple install floraconcierge api client into your django environment by adding middleware
`floraconcierge.middleware.ApiClientMiddleware` to your `MIDDLEWARE_CLASSES`.

Also you can add `floraconcierge.middleware.ApiObjectNotFound404` to your middlewares for automatic 404 pages when
api result raises ResultObjectNotFoundError.

Available settings
------------------

All settings used in middleware only, if you want manual initiation of api client object, you can do it yourself.

* `FLORACONCIERGE_API_ID` Required. Your application ID.

* `FLORACONCIERGE_API_SECRET` Required. Your application secret.

* `FLORACONCIERGE_API_INIT_ENV` Optional. You can setup custom init function for env setup. Function takes params
`client, request, restored` where client is ApiClient instance, request is django request object and restored is flag
variable indicating client env was restored from request session.

* `FLORACONCIERGE_API_INIT_CLIENT` Optional. Custom api client initiation function. By default middleware initiate
client with function `floraconcierge.middleware.initialize_apiclient`. You can se your own function. Function take
only one param `request`.

* `FLORACONCIERGE_PRODUCT_IMAGES` Optional. Can be used to customize product images urls by this dict. Generated urls added automatically to
product `urls` field. You can get product image url with `product.urls['thumb']` or in Django Template by calling
`{{ product.urls.thumb }}`. Available default sizes: default, small, middle, big, thumb_100, thumb_250, thumb_500.

Django debug toolbar panel
--------------------------

Also available debug panel for django.

You can add `floraconcierge.panels.FloraConciergeRequests` to django debug panels settings `DEBUG_TOOLBAR_PANELS`.

And you must add `floraconcierge` to your `INSTALLED_APPS`.

Collection methods
------------------

Now you can search throught your result collections with find/findall methods.

Request cache middleware
------------------------

FloraConcierge api provides simple request lifetime cache object for caching offen queried data on page. This cache
cleares automatically every next request.

You can add `floraconcierge.middleware.RequestCacheMiddleware` to your `MIDDLEWARE_CLASSES` and get request cache
instance with function `floraconcierge.cache.get_request_cache()`.

You must inherit your cache object from `floraconcierge.cache.RequestCache` and setup it via `FLORACONCIERGE_CACHE_CLASS`.

ApiAuth authentication backend
------------------------------

You can add support for logging in users on your site with api by adding `floraconcierge.apiauth` to your `INSTALLED_APPS`.

After application installation to your apps, you must add `floraconcierge.apiauth.backends.FloraConciergeBackend` to
your `AUTHENTICATION_BACKENDS`.

After this users will can login on your site throught floraconcierge api by standart django authentication framework.