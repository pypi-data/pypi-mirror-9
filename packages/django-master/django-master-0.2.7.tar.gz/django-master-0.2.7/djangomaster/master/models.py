from django.conf import settings

from djangomaster.utils import get_module, is_model
from djangomaster.views import MasterView


class ModelsView(MasterView):
    name = 'models'
    label = 'Models'
    title = 'Models'
    template_name = 'djangomaster/sbadmin/pages/models.html'

    def get_context_data(self):
        context = super(ModelsView, self).get_context_data()
        modules = []

        for appname in settings.INSTALLED_APPS:
            module = get_module(appname)
            if hasattr(module, 'models'):
                modules.append(ModuleInstance(module))

        context['modules'] = modules
        return context


class ModuleInstance(object):
    def __init__(self, module):
        self.module = module
        self._models = None

    @property
    def name(self):
        return self.module.__name__

    @property
    def models(self):
        if self._models is None:
            self._models = []
            for name, item in self.module.models.__dict__.items():
                if hasattr(item, '__base__') and is_model(item):
                    self._models.append(ModelInstance(item))

        return self._models


class ModelInstance(object):
    def __init__(self, model):
        self.model = model

    @property
    def name(self):
        return self.model.__name__

    @property
    def fields(self):
        return [FieldInstance(f) for f in self.model._meta.fields]

    @property
    def count(self):
        return self.model.objects.count()

    def is_abstract(self):
        return self.model._meta.abstract


class FieldInstance(object):
    def __init__(self, field):
        self.field = field

    @property
    def name(self):
        return self.field.attname

    @property
    def type(self):
        clsname = str(type(self.field))
        return clsname[8:-2]

    @property
    def help_text(self):
        return self.field.help_text


