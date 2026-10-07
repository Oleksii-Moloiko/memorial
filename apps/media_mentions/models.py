from django.db import models


class MediaMention(models.Model):
    class Category(models.TextChoices):
        OFFICIAL = "official", "Офіційне джерело"
        PRESS = "press", "ЗМІ"

    service_page = models.ForeignKey(
        "pages.ServicePage",
        verbose_name="Подвиг і служба",
        related_name="mentions",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    title = models.CharField(
        "Заголовок матеріалу",
        max_length=255,
    )
    source_name = models.CharField(
        "Назва джерела",
        max_length=255,
    )
    category = models.CharField(
        "Категорія",
        max_length=20,
        choices=Category.choices,
        default=Category.PRESS,
    )
    url = models.URLField(
        "Посилання",
    )
    preview_image = models.ImageField(
        "Зображення прев’ю",
        upload_to="media_mentions/previews/manual/",
        blank=True,
        null=True,
        help_text=(
            "Необов’язково. Якщо завантажити зображення вручну, "
            "воно матиме пріоритет над автоматичним прев’ю."
        ),
    )

    auto_preview_image = models.ImageField(
        "Автоматичне прев’ю",
        upload_to="media_mentions/previews/auto/",
        blank=True,
        null=True,
        editable=False,
    )

    preview_variants = models.JSONField(
        "Оптимізовані копії прев’ю",
        default=dict,
        blank=True,
        editable=False,
    )

    preview_fetched_from = models.URLField(
        "Джерело автоматичного прев’ю",
        max_length=2048,
        blank=True,
        editable=False,
    )

    preview_fetched_at = models.DateTimeField(
        "Прев’ю отримано",
        null=True,
        blank=True,
        editable=False,
    )
    published_date = models.DateField(
        "Дата публікації",
        null=True,
        blank=True,
    )
    is_published = models.BooleanField(
        "Показувати на сайті",
        default=True,
    )
    is_featured = models.BooleanField(
        "Показувати на головній",
        default=False,
        help_text="Рекомендовано вибрати лише один матеріал.",
    )
    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_featured:
            MediaMention.objects.exclude(pk=self.pk).filter(
                is_featured=True,
            ).update(is_featured=False)

    @property
    def effective_preview(self):
        return self.preview_image or self.auto_preview_image

    @property
    def responsive_preview(self):
        source = self.effective_preview
        manifest = self.preview_variants or {}

        if (
            not source
            or manifest.get("source") != source.name
            or not manifest.get("variants")
        ):
            return None

        formats = {}

        for extension in ("webp", "jpg"):
            by_width = {}

            for variant in manifest["variants"]:
                if variant["format"] != extension:
                    continue

                width = variant["width"]
                current = by_width.get(width)

                if current is None or variant["bytes"] < current["bytes"]:
                    by_width[width] = variant

            formats[extension] = [
                {
                    **variant,
                    "url": source.storage.url(variant["name"]),
                }
                for _, variant in sorted(by_width.items())
            ]

        if not formats["jpg"] or not formats["webp"]:
            return None

        largest_jpeg = formats["jpg"][-1]

        return {
            "src": largest_jpeg["url"],
            "width": largest_jpeg["width"],
            "height": largest_jpeg["height"],
            "jpeg_srcset": ", ".join(
                f"{variant['url']} {variant['width']}w"
                for variant in formats["jpg"]
            ),
            "webp_srcset": ", ".join(
                f"{variant['url']} {variant['width']}w"
                for variant in formats["webp"]
            ),
        }

    class Meta:
        verbose_name = "Публікація"
        verbose_name_plural = "Публікації"
        ordering = ["order", "-published_date"]

    def __str__(self) -> str:
        return self.title
