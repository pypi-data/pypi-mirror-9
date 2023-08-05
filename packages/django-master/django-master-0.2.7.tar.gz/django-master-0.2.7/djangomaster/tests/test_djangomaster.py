import os
from mock import patch

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from djangomaster import get_version, get_urls
from djangomaster.factories import UserFactory


class TestDjangoMaster(TestCase):

    def test_get_version(self):
        path = os.path.join(settings.BASE_DIR, 'djangomaster', 'version.txt')
        version = open(path).read().strip()

        self.assertEqual(version, get_version())

    @patch('djangomaster.autodiscover')
    def test_get_urls(self, autodiscover_mock):
        ret = get_urls()
        self.assertTrue(autodiscover_mock.called)

        self.assertIsInstance(ret[0], list)
        self.assertEqual(ret[1], 'djangomaster')
        self.assertEqual(ret[2], 'djangomaster')

    def test_redirect_to_djangomaster_home(self):
        user = UserFactory(is_superuser=True)
        self.client.login(username=user.username, password='adm1n')

        response = self.client.get('/master/')
        url = reverse('djangomaster:djangomaster-home')
        self.assertRedirects(response, url, status_code=301)
