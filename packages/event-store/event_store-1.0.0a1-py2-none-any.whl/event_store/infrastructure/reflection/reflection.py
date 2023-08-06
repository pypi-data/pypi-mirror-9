__author__ = 'Andriy Drozdyuk'


def get_class( kls ):
    """Get class given a fully qualified name of a class"""
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__( module )
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def obj_name(obj):
    """Fully qualified name of an object"""
    return '%s.%s' % (obj.__class__.__module__, obj.__class__.__name__)


def cls_name(cls):
    """Fully qualified name of a class"""
    return '%s.%s' % (cls.__module__, cls.__name__)
