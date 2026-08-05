from django.db import models


class MediaMention(models.Model):
    source_name = models.CharField("Джерело", max_length=255)
    url = models.URLField("Посилання")
    published_date = models.DateField("Дата публікації", null=True, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Згадка в медіа"
        verbose_name_plural = "Згадки в медіа"
        ordering = ["order", "-published_date"]

    def __str__(self):
        return self.source_name
