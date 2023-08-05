from django.test import TestCase

from djangomaster.sites import MasterSite
from djangomaster.views import MasterView
from djangomaster.widgets import MasterWidget


class TestMasterSite(TestCase):

    def setUp(self):
        self.mastersite = MasterSite()

    def test_add_view(self):
        class Yeah(MasterView):
            pass

        self.mastersite.add_view('one', Yeah)

        self.assertEqual(len(self.mastersite.pages['one']), 1)
        self.assertEqual(self.mastersite.pages['one'][0], Yeah)

    def test_add_widget(self):
        class Yeah(MasterWidget):
            pass

        self.mastersite.add_widget('two', Yeah)

        self.assertEqual(len(self.mastersite.widgets['two']), 1)
        self.assertEqual(self.mastersite.widgets['two'][0], Yeah)
