from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Керування меморіальним сайтом"
admin.site.site_title = "Адмінка меморіалу"
admin.site.index_title = "Матеріали та налаштування"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
