from django.core.cache import cache
from django.db import models


class SiteSettings(models.Model):
    """Singleton з глобальними налаштуваннями сайту.

    Використовується через SiteSettings.load(), доступний у будь-якому
    шаблоні як `site_settings` завдяки config.context_processors.site_settings.
    """

    site_title = models.CharField(
        "Назва сайту",
        max_length=200,
        default="Memorial",
    )
    brand_letter = models.CharField("Літера логотипа", max_length=4, blank=True)
    site_name = models.CharField("Назва в шапці", max_length=100, blank=True)
    subtitle = models.CharField("Підзаголовок у шапці", max_length=200, blank=True)
    footer_text = models.TextField("Текст у футері", blank=True)
    copyright_holder = models.CharField(
        "Правовласник у копірайті", max_length=200, blank=True
    )
    demo_strip_enabled = models.BooleanField(
        "Показувати демо-плашку",
        default=True,
        help_text="Стрічка «Демонстраційний макет» під шапкою. Вимкнути перед передачею родині.",
    )

    class Meta:
        verbose_name = "Налаштування сайту"
        verbose_name_plural = "Налаштування сайту"

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete("site_settings")

    def delete(self, *args, **kwargs):
        pass  # singleton — не видаляється

    @classmethod
    def load(cls):
        cached = cache.get("site_settings")
        if cached is not None:
            return cached
        obj, _ = cls.objects.get_or_create(pk=1)
        cache.set("site_settings", obj, 300)
        return obj
