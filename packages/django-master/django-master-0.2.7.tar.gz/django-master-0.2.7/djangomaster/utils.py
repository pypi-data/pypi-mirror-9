from django.db.models import Model
from django.dispatch import Signal


def is_model(cls):
    """Given the class, checks if it is or any base
    class is the `django.db.models.Model` class"""
    if cls is Model:
        return True

    for basecls in cls.__bases__:
        if is_model(basecls):
            return True


def is_signal(instance):
    """Given the instance, checks if it is or any
    base class is the Signal class """
    cls = getattr(instance, '__class__', instance)

    if cls in (type, object):
        return False

    if cls == Signal:
        return True

    for base in cls.__bases__:
        if is_signal(base):
            return True

    return False


def get_module(module_name):
    paths = module_name.split('.')
    module = __import__(module_name)
    for path in paths[1:]:
        module = getattr(module, path)
    return module
