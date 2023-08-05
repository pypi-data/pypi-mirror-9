from djangomaster.conf import settings
from djangomaster.utils import get_module, is_signal
from djangomaster.views import MasterView

SIGNAL_MODULES = (
    'django.core.signals',
    'django.contrib.auth.signals',
    'django.test.signals',
    'django.db.models.signals',
    'django.db.backends.signals',
    'django.contrib.comments.signals',
) + settings.SIGNAL_MODULES


class SignalsView(MasterView):
    name = 'signals'
    label = 'Signals'
    title = 'Signals'
    template_name = 'djangomaster/sbadmin/pages/signals.html'

    def get_context_data(self):
        context = super(SignalsView, self).get_context_data()
        context['conf_name'] = 'DJANGOMASTER_SIGNAL_MODULES'

        ret = []
        for module_name in SIGNAL_MODULES:
            module = get_module(module_name)
            for name, item in module.__dict__.items():
                if is_signal(item):
                    ret.append(SignalInstance(item, name=name,
                                              module=module_name))

        context['signals'] = ret
        return context


class SignalInstance:

    def __init__(self, instance, name='', module=''):
        self.instance = instance
        self._name = name
        self._module = module

    @property
    def name(self):
        cls_name = self._module
        if self._name:
            cls_name += '.' + self._name
        return cls_name

    @property
    def receivers(self):
        ret = []
        for receiver in self.instance.receivers:
            ret.append(Receiver(receiver))
        return ret

    def has_receivers(self):
        return len(self.instance.receivers) > 0


class Receiver:

    def __init__(self, receiver):
        self.receiver = receiver
        self._func = receiver[1]()

    @property
    def name(self):
        return self._func.func_name

    @property
    def file_name(self):
        return "%s:%s" % (self._func.func_code.co_filename,
                          self._func.func_code.co_firstlineno)
