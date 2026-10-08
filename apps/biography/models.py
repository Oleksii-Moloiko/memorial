from django.db import models


class Biography(models.Model):
    """Життєпис. Singleton (одна людина = один сайт)."""

    full_name = models.CharField("ПІБ", max_length=255)
    rank = models.CharField(
        "Звання",
        max_length=255,
        blank=True,
        help_text="Наприклад: «Старший лейтенант, командир взводу»",
    )
    birth_date = models.DateField("Дата народження", null=True, blank=True)
    death_date = models.DateField("Дата смерті", null=True, blank=True)
    portrait = models.ImageField(
        "Портрет", upload_to="biography/", null=True, blank=True
    )
    portrait_variants = models.JSONField(
        "Оптимізовані копії портрета",
        default=dict,
        blank=True,
        editable=False,
    )
    award_title = models.CharField(
        "Нагорода (коротко)",
        max_length=255,
        blank=True,
        help_text="Наприклад: «Герой України»",
    )
    intro_text = models.TextField("Вступний текст на головній", blank=True)
    signature_quote = models.CharField("Головна цитата", max_length=500, blank=True)
    summary = models.TextField("Короткий опис (для головної)", blank=True)
    full_text = models.TextField("Повний життєпис", blank=True)

    class Meta:
        verbose_name = "Життєпис"
        verbose_name_plural = "Життєпис"

    def __str__(self):
        return self.full_name

    @property
    def responsive_portrait(self):
        manifest = self.portrait_variants or {}

        if (
            not self.portrait
            or manifest.get("source") != self.portrait.name
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
                    "url": self.portrait.storage.url(variant["name"]),
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

class TimelineEvent(models.Model):
    """Подія хронології життя."""

    biography = models.ForeignKey(
        Biography,
        on_delete=models.CASCADE,
        related_name="timeline_events",
        verbose_name="Життєпис",
    )

    date_label = models.CharField(
        "Дата / період",
        max_length=50,
    )

    title = models.CharField(
        "Заголовок події",
        max_length=255,
    )

    description = models.CharField(
        "Опис",
        max_length=500,
        blank=True,
    )

    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )

    class Meta:
        verbose_name = "Подія хронології"
        verbose_name_plural = "Хронологія"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.date_label} — {self.title}"
