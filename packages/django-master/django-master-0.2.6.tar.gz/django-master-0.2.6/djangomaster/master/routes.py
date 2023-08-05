from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch

from djangomaster.views import MasterView


class Route(object):
    """ Wraps a RegexURLPattern or RegexURLResolver to create
    a common interface """

    def __init__(self, obj, app_name='', base=''):
        self.obj = obj
        self.base = base
        self._app_name = app_name

    @property
    def name(self):
        return getattr(self.obj, 'name', '')

    @property
    def app_name(self):
        _app_name = getattr(self.obj, 'app_name', None)
        return _app_name or self._app_name

    @property
    def url(self):
        return "%s %s" % (self.base, self.obj.regex.pattern)

    @property
    def view(self):
        if getattr(self.obj, 'callback', None):
            return "%s.%s" % (self.obj.callback.__module__,
                              self.obj.callback.__name__)
        elif getattr(self.obj, '_get_callback', None):
            return "%s.%s" % (self.obj._get_callback().__module__,
                              self.obj._get_callback().__name__)
        elif getattr(self.obj, 'urlconf_module', None):
            return self.obj.urlconf_module.__name__
        else:
            return ''

    @property
    def sub_urls(self):
        urls = getattr(self.obj, 'url_patterns', [])
        routes = [Route(url, base=self.url, app_name=self.app_name)
                  for url in urls]
        return sorted(routes, key=lambda x: x.url)

    @property
    def args(self):
        ret = []
        keys = self.obj.regex.groupindex.keys()
        for i in range(self.args_count):
            try:
                ret.append((i, keys[i]))
            except IndexError:
                ret.append((i, ''))
        return ret

    @property
    def args_count(self):
        return self.obj.regex.groups

    @property
    def url_reversed(self):
        app_name = self.app_name
        name = self.name
        if app_name:
            name = app_name + ':' + name

        try:
            return reverse(name)
        except NoReverseMatch:
            return ''


class RoutesView(MasterView):
    name = 'routes'
    label = 'Routes'
    title = 'Routes'
    template_name = 'djangomaster/sbadmin/pages/routes.html'

    def get_context_data(self):
        context = super(RoutesView, self).get_context_data()
        root_urls = __import__(settings.ROOT_URLCONF)
        ret = []

        for url in root_urls.urls.urlpatterns:
            ret.append(Route(url))

        ret = sorted(ret, key=lambda x: x.url)

        context['routes'] = ret
        return context
