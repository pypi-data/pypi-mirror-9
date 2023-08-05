from django.conf import settings as djangosettings
from django.core.exceptions import ImproperlyConfigured


class Settings(object):
    conf = djangosettings

    def get(self, prop_name, default_value):
        prop_name = 'DJANGOMASTER_%s' % prop_name
        return getattr(self.conf, prop_name, default_value)

    @property
    def BASE_DIR_NAME(self):
        return self.get('BASE_DIR', 'BASE_DIR')

    @property
    def BASE_DIR(self):
        return getattr(self.conf, self.BASE_DIR_NAME, None)

    @property
    def REQUIREMENTS_TXT(self):
        return self.get('REQUIREMENTS_NAME', 'requirements.txt')

    @property
    def SOUTH_IS_INSTALLED(self):
        return 'south' in self.conf.INSTALLED_APPS

    @property
    def SIGNAL_MODULES(self):
        modules = self.get('SIGNAL_MODULES', ())
        if type(modules) not in (tuple, list):
            raise ImproperlyConfigured('DJANGOMASTER_SIGNAL_MODULES must be '
                                       'a tuple')
        return modules


settings = Settings()
