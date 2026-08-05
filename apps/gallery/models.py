from django.db import models


class Photo(models.Model):
    class LayoutSize(models.TextChoices):
        NORMAL = "", "Звичайний"
        TALL = "span-tall", "Високий"
        WIDE = "span-wide", "Широкий"

    image = models.ImageField("Фото", upload_to="gallery/")
    caption = models.CharField("Підпис", max_length=255, blank=True)
    layout_size = models.CharField(
        "Розмір у сітці", max_length=20, choices=LayoutSize.choices, blank=True
    )
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фотогалерея"
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"Фото #{self.pk}"
