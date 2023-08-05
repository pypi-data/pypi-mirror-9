from collections import defaultdict

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from django.template.defaultfilters import slugify
from django.views.generic.base import RedirectView


class MasterSite(object):
    def __init__(self):
        self.pages = defaultdict(list)
        self.widgets = defaultdict(list)
        self._menu = OrderedDict()

    @property
    def homeview(self):
        homeurl = reverse_lazy('djangomaster:djangomaster-home')
        return RedirectView.as_view(url=homeurl)

    @property
    def urlpatterns(self):
        self._menu = OrderedDict()
        urls = [url(r'^$', self.homeview, name='djangomaster')]

        for module, pages in self.pages.items():
            module = module.replace('.master', '')
            self._menu[module] = []
            module_name = slugify(module)

            for page in pages:
                page_name = slugify(page.name)
                page.slug = module_name + '-' + page_name
                pattern = r'^{module}/{page}'.format(module=module_name,
                                                     page=page_name)
                urls.append(url(pattern, page.as_view(), name=page.slug))

                self._menu[module].append({
                    'name': page.slug,
                    'label': page.label
                })

        return patterns(r'', *urls)

    def add_view(self, module_name, view):
        if view.abstract is False:
            self.pages[module_name].append(view)

    def add_widget(self, module_name, widget):
        if widget.abstract is False:
            self.widgets[module_name].append(widget)

    def get_menu(self):
        if not self._menu:
            self.urlpatterns
        return self._menu

mastersite = MasterSite()
