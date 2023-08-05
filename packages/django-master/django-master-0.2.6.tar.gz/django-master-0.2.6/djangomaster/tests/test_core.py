from django.test import TestCase

from djangomaster.core import is_widget, is_view, autodiscover
from djangomaster.sites import MasterSite
from djangomaster.views import MasterView
from djangomaster.widgets import MasterWidget


class TestIsWidget(TestCase):
    master_class = MasterWidget
    method = lambda self, cls: is_widget(cls)

    def test_with_empty_class(self):
        class Nada(object):
            pass

        self.assertFalse(self.method(Nada))

    def test_with_correct_class(self):
        class Yeah(self.master_class):
            pass

        self.assertTrue(self.method(Yeah))

    def test_with_subclasses(self):
        class NopeWidget(self.master_class):
            pass

        class NopeNopeWidget(NopeWidget):
            pass

        class NopeNopeNopeWidget(NopeNopeWidget):
            pass

        self.assertTrue(self.method(NopeWidget))
        self.assertTrue(self.method(NopeNopeWidget))
        self.assertTrue(self.method(NopeNopeNopeWidget))


class TestIsPage(TestIsWidget):
    master_class = MasterView
    method = lambda self, cls: is_view(cls)


class TestAutodiscover(TestCase):

    def setUp(self):
        self.site = MasterSite()

    def test_simple(self):
        autodiscover(site=self.site)
