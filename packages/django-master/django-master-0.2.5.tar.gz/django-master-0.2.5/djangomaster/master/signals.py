from django.dispatch import Signal

from djangomaster.conf import settings
from djangomaster.views import MasterView

SIGNAL_MODULES = (
    'django.core.signals',
    'django.contrib.auth.signals',
    'django.test.signals',
    'django.db.models.signals',
    'django.db.backends.signals',
    'django.contrib.comments.signals',
) + settings.SIGNAL_MODULES


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


class SignalsView(MasterView):
    name = 'signals'
    label = 'Signals'
    title = 'Signals'
    template_name = 'djangomaster/sbadmin/pages/signals.html'

    def get_context_data(self):
        context = super(SignalsView, self).get_context_data()

        ret = []
        for module_name in SIGNAL_MODULES:
            module = get_module(module_name)
            for name, item in module.__dict__.items():
                if is_signal(item):
                    ret.append(SignalInstance(item, name=name,
                                              module=module_name))

        context['signals'] = ret
        return context

    def get_footer(self):
        return ("You can add modules to be watched adding them "
                "to `{conf_name}` settings. ex: <br />"
                "<code>{conf_name} = ('amazingapp.signals', "
                "'anotherapp.models', )</code>"
                "").format(conf_name='DJANGOMASTER_SIGNAL_MODULES')


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
