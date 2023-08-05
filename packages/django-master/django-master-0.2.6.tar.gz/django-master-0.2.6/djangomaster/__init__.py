import os

from djangomaster.core import autodiscover
from djangomaster.sites import mastersite


def get_version():
    path = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(path, 'version.txt')
    return open(path).read().strip()

__version__ = get_version()


def get_urls():
    autodiscover()
    return mastersite.urlpatterns, 'djangomaster', 'djangomaster'

urls = get_urls()
