import djangomaster

from django.conf import settings
from django.conf.urls import patterns, url, include
from django.conf.urls.static import static
from django.contrib import admin


# admin.autodiscover()


urlpatterns = patterns(
    r'',

    url(r'^admin/', include(admin.site.urls)),
    url(r'^master/', include(djangomaster.urls)),

)


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
