import inspect

from djangomaster.sites import mastersite
from djangomaster.views import MasterView
from djangomaster.widgets import MasterWidget


def autodiscover(site=mastersite):
    """
    based on: https://github.com/django/django/blob/1.4.16/django/
              contrib/admin/__init__.py

    looks in all INSTALLED_APPS for the master module and load all
    widget and pages
    """

    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    site.__init__()
    modules = []

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)

        try:
            module_name = '%s.master' % app
            modules.append(import_module(module_name))
        except:
            if module_has_submodule(mod, 'master'):
                raise

    for module in modules:
        for name, item in inspect.getmembers(module):
            if is_view(item):
                site.add_view(module.__name__, item)
            elif is_widget(item):
                site.add_widget(module.__name__, item)


def is_widget(cls):
    """ Checks if the given classe has MasterWidget as base """
    return _is_base_of(cls, MasterWidget)


def is_view(cls):
    """ Checks if the given classe has MasterView as base """
    return _is_base_of(cls, MasterView)


def _is_base_of(cls, masterbase):
    bases = getattr(cls, '__bases__', ())
    if masterbase in bases:
        return True

    for base in bases:
        if _is_base_of(base, masterbase):
            return True

    return False
