from django.db import models


class SeoPage(models.Model):
    """SEO-метадані для однієї сторінки сайту.

    page_key відповідає {% block page_key %} у base.html / іменам маршрутів
    у apps.pages.urls (home, life, service, photos, videos, media, memories).
    """

    page_key = models.SlugField("Ключ сторінки", unique=True)
    title = models.CharField("Title", max_length=255, blank=True)
    description = models.CharField("Meta description", max_length=320, blank=True)
    og_image = models.ImageField(
        "OG-зображення", upload_to="seo/", null=True, blank=True
    )

    class Meta:
        verbose_name = "SEO сторінки"
        verbose_name_plural = "SEO сторінок"

    def __str__(self):
        return self.page_key
