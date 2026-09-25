from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.contrib.sitemaps.views import sitemap

from apps.seo.sitemaps import StaticViewSitemap
from apps.seo.views import robots_txt

handler404 = "apps.pages.views.custom_404"

sitemaps = {
    "static": StaticViewSitemap,
}

admin.site.site_header = "Керування меморіальним сайтом"
admin.site.site_title = "Адмінка меморіалу"
admin.site.index_title = "Керування меморіальним сайтом"

urlpatterns = [
    path(
        "robots.txt",
        robots_txt,
        name="robots",
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemap",
    ),
    path("admin/", admin.site.urls),
]


urlpatterns += i18n_patterns(
    path("i18n/", include("django.conf.urls.i18n")),
    path("", include("apps.pages.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
