import os
from importlib import import_module

from django.conf import settings

from djangomaster.views import MasterView


MODULE = type(os)


class TemplateTagsView(MasterView):
    name = 'templatetags'
    label = 'Template Tags'
    title = 'Template Tags'
    template_name = 'djangomaster/sbadmin/pages/templatetags.html'

    def get_context_data(self):
        context = super(TemplateTagsView, self).get_context_data()

        ret = []
        for app in settings.INSTALLED_APPS:
            try:
                module_name = app + '.templatetags'
                mod = import_module(module_name)
                ret.append(ModuleTag(mod, name=module_name))
            except ImportError:
                pass

        context['tags'] = ret
        return context


class ModuleTag(object):

    def __init__(self, mod, name):
        self.mod = mod
        self.module_name = name
        self._tags = None
        self._filters = None

    @property
    def name(self):
        return self.mod.__name__

    @property
    def filepath(self):
        return self.mod.__file__

    @property
    def tags(self):
        if self._tags is None:
            self._setup()

        return self._tags

    @property
    def filters(self):
        if self._filters is None:
            self._setup()

        return self._filters

    def _setup(self):
        self._tags = []
        self._filters = []
        valid_mods = []

        path = self.mod.__path__[0]
        for root, dirs, files in os.walk(path):
            for filename in files:
                if filename.endswith('.py'):
                    mod_name = self.module_name + '.' + filename[:-3]
                    try:
                        mod = import_module(mod_name)
                        if hasattr(mod, 'register'):
                            valid_mods.append(mod)
                    except ImportError:
                        pass

        for mod in valid_mods:
            for name, func in mod.register.tags.items():
                tag = Tag(name, func, module=mod)
                self._tags.append(tag)

            for name, func in mod.register.filters.items():
                f = Filter(name, func, module=mod)
                self._filters.append(f)


class Tag(object):

    def __init__(self, name, func, module=None):
        self.name = name
        self._func = func
        self.module = module


class Filter(object):

    def __init__(self, name, func, module=None):
        self.name = name
        self._func = func
        self.module = module
