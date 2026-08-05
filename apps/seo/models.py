from django.db import models


class SeoPage(models.Model):
    """SEO-метадані для однієї сторінки сайту.

    page_key відповідає {% block page_key %} у base.html / іменам маршрутів
    у apps.pages.urls (home, life, service, photos, videos, media, memories).
    """

    class PageKey(models.TextChoices):
        HOME = "home", "Головна"
        LIFE = "life", "Життя"
        SERVICE = "service", "Подвиг і служба"
        PHOTOS = "photos", "Фото"
        VIDEOS = "videos", "Відео"
        MEDIA = "media", "У ЗМІ"
        MEMORIES = "memories", "Спогади"

    page_key = models.CharField(
        "Сторінка", max_length=20, choices=PageKey.choices, unique=True
    )
    title = models.CharField("Title", max_length=255, blank=True)
    description = models.CharField("Meta description", max_length=320, blank=True)
    og_image = models.ImageField(
        "OG-зображення", upload_to="seo/", null=True, blank=True
    )

    class Meta:
        verbose_name = "SEO сторінки"
        verbose_name_plural = "SEO сторінок"

    def __str__(self):
        return self.get_page_key_display()
