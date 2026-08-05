from django.conf import settings
from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("life/", views.life, name="life"),
    path("service/", views.service, name="service"),
    path("photos/", views.photos, name="photos"),
    path("videos/", views.videos, name="videos"),
    path("media/", views.media, name="media"),
    path("memories/", views.memories, name="memories"),
]

if settings.DEBUG:
    # Дизайн-концепт показуємо тільки в розробці, у проді сторінки не існує.
    urlpatterns += [path("styleguide/", views.styleguide, name="styleguide")]
