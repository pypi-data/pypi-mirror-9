from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic.detail import View

from djangomaster.sites import mastersite
from djangomaster.conf import settings as mastersettings


class MasterView(View):
    name = 'base'
    label = 'Django Master'
    title = 'Django Master'
    template_name = 'djangomaster/base.html'
    abstract = False
    widgets = ()

    def get_title(self):
        return self.title

    def get_widgets(self):
        return self.widgets

    def get_menu(self):
        return mastersite.get_menu()

    def get_context_data(self, **kwargs):
        item_name = getattr(self, 'slug', '')

        context = {
            'title': self.get_title(),
            'widgets': self.get_widgets(),
            'mastermenu': self.get_menu(),
            'mastermenu_module': item_name.split('-')[0],
            'mastermenu_item': item_name,
            'params': kwargs,
            'settings': mastersettings,
        }

        return context

    def render_to_response(self, context):
        return render(self.request, self.template_name, context)

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied

        return super(MasterView, self).dispatch(request, *args, **kwargs)
