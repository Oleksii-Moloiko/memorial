from django.db import models


class Video(models.Model):
    title = models.CharField("Назва", max_length=255, blank=True)
    embed_url = models.URLField("Посилання (YouTube/Vimeo embed)")
    thumbnail = models.ImageField(
        "Превʼю", upload_to="videos/", null=True, blank=True
    )
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Відео"
        verbose_name_plural = "Відео"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title or f"Відео #{self.pk}"
