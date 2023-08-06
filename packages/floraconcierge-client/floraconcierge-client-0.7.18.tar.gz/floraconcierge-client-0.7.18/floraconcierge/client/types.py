from importlib import import_module
from pprint import pformat
from datetime import datetime

from pytz import timezone

from floraconcierge import errors


MIN_INT_TO_DATETIME = 500000000
# If int value is greater then this constant, object will have field ${field}_date which will be datetime type.
# Date 05.11.1985. Too big value for usual usage and fine date :)


def module_name_from_class(cls):
    class_name = ('floraconcierge.mapping.%s' % cls.replace("_", '.').lower()).split('.')
    module, name = ".".join(class_name[:-1]), class_name[-1].capitalize()

    return module, name


def from_dict(obj):
    """
    Creates floraconcierge api result object instance
    @param obj: dict
    @return: Object
    """
    if '_className' in obj and obj['_className']:
        module, name = module_name_from_class(obj['_className'])

        try:
            m = import_module(module)
            cls = getattr(m, name)
        except (ImportError, AttributeError):
            errtpl = '%s.%s for api "%s" mapping not found'
            raise errors.ModelMappingNotFoundError(errtpl % (module, name, obj['_className']))

        return cls(**obj)

    return Object(**obj)


class Object(object):
    def __init__(self, *args, **kwargs):
        super(Object, self).__init__()

        if '_className' in kwargs:
            del kwargs['_className']

        extra = {}
        for k, v in kwargs.iteritems():
            if not isinstance(v, (int, float)):
                try:
                    v = int(v)
                except (ValueError, TypeError):
                    try:
                        v = float(v)
                    except (ValueError, TypeError):
                        pass

            magic_date = '%s_date' % k
            if isinstance(v, (int, float)) and v > MIN_INT_TO_DATETIME and magic_date not in kwargs:
                try:
                    extra[magic_date] = datetime.fromtimestamp(v, timezone('Europe/Moscow'))
                except:
                    extra[magic_date] = None

            kwargs[k] = v

        self.__dict__.update(kwargs)
        self.__dict__.update(extra)

    def __repr__(self):
        if not hasattr(self, '_repr_cache'):
            setattr(self, '_repr_cache', '<%s %s>' % (self.__class__.__name__, pformat(self.__dict__)))

        return getattr(self, '_repr_cache')

    def __iter__(self):
        if hasattr(super(Object, self), '__iter__'):
            # noinspection PyUnresolvedReferences
            return super(Object, self).__iter__()

        return self.__dict__.copy().iteritems()

    def todict(self):
        data = self.__dict__
        data.pop('_repr_cache', None)

        return data

    def datetime(self, unixtime):
        return datetime.fromtimestamp(int(unixtime))
