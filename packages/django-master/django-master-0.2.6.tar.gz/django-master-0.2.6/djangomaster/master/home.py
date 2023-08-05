import os
from datetime import datetime, timedelta

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.conf import settings, global_settings

from djangomaster.conf import settings as mastersettings
from djangomaster.views import MasterView
from djangomaster.widgets import MasterWidget


# Widgets


class RequirementsWidget(MasterWidget):
    template_name = 'djangomaster/sbadmin/widget/textarea.html'
    title = 'requirements.txt'

    def get_context_data(self):
        context = super(RequirementsWidget, self).get_context_data()

        if mastersettings.BASE_DIR is None:
            return self._return_basedir_error()

        path = os.path.join(mastersettings.BASE_DIR,
                            mastersettings.REQUIREMENTS_TXT)
        if not os.path.isfile(path):
            return self._return_path_error(path)

        context['content'] = open(path).read()
        return context

    def _return_basedir_error(self):
        msg = ('Define the settings.{} variable, then it will be possible '
               ' to locate the requirements.txt file.')
        html = ('Add the following in your settings.py:<br />'
                '<code>BASE_DIR = '
                'os.path.dirname(os.path.abspath(__file__))</code> <br />'
                'You can define which variable will be used'
                'by changing `settings.DJANGOMASTER_BASE_DIR`.')

        return {
            'error': msg.format(settings.BASE_DIR_NAME),
            'html': html
        }

    def _return_path_error(self, path):
        msg = 'Could not find a file in {}'
        return {'error': msg.format(path)}


class UserCountWidget(MasterWidget):
    template_name = 'djangomaster/sbadmin/widget/table.html'
    title = 'Users\' info'

    def get_context_data(self):
        context = super(UserCountWidget, self).get_context_data()

        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
        except ImportError:
            from django.contrib.auth.models import User

        days = datetime.now() - timedelta(days=14)
        signup_count = User.objects.filter(date_joined__gte=days).count()

        rows = []
        rows.append(['Users signed in last two weeks:', signup_count])
        rows.append(['Total users:', User.objects.count()])

        context['table'] = {'rows': rows}

        return context


# Views


class HomeView(MasterView):
    name = 'home'
    label = 'Home'
    title = 'Django Master'
    template_name = 'djangomaster/sbadmin/home.html'
    widgets = (RequirementsWidget, UserCountWidget, )


class SettingsView(MasterView):
    name = 'settings'
    label = 'Settings'
    title = 'Settings'
    template_name = 'djangomaster/sbadmin/pages/settings.html'

    def get_context_data(self):
        context = super(SettingsView, self).get_context_data()

        context['dict'] = OrderedDict()
        items = settings._wrapped.__dict__.items()

        for key, value in sorted(items, key=lambda key: key):
            context['dict'][key] = {
                'value': value,
                'changed': self._settings_has_changed(key, value)
            }

        return context

    def _settings_has_changed(self, key, value):
        if not hasattr(global_settings, key):
            return True

        original_value = getattr(global_settings, key)
        return original_value != value
