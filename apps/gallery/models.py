from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class Photo(models.Model):
    class Category(models.TextChoices):
        FAMILY = "family", _("Сім’я та дитинство")
        STUDY = "study", _("Навчання")
        SERVICE = "service", _("Служба та побратими")
        MEMORY = "memory", _("Вшанування")

    class LayoutSize(models.TextChoices):
        NORMAL = "", "Автоматично"
        TALL = "span-tall", "Вертикальне 9:16"
        WIDE = "span-wide", "Горизонтальне 16:9"

    image = models.ImageField(
        "Фото",
        upload_to="gallery/",
    )

    image_variants = models.JSONField(
        "Оптимізовані копії",
        default=dict,
        blank=True,
        editable=False,
    )

    caption = models.CharField(
        "Підпис",
        max_length=255,
        blank=True,
    )

    alt_text = models.CharField(
        "Опис зображення",
        max_length=255,
        blank=True,
        help_text=("Короткий опис для людей, які використовують екранні читачі."),
    )

    category = models.CharField(
        "Категорія",
        max_length=20,
        choices=Category.choices,
        default=Category.FAMILY,
        help_text=("Визначає, у якій категорії фото буде показане на сторінці."),
    )

    layout_size = models.CharField(
        "Формат у галереї",
        max_length=20,
        choices=LayoutSize.choices,
        blank=True,
        help_text=(
            "Визначає форму прев’ю фото в галереї. "
            "У більшості випадків залишайте «Автоматично»."
        ),
    )

    preview_focus_x = models.PositiveSmallIntegerField(
        "Фокус прев’ю по горизонталі",
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0 — лівий край, 100 — правий край.",
    )

    preview_focus_y = models.PositiveSmallIntegerField(
        "Фокус прев’ю по вертикалі",
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="0 — верхній край, 100 — нижній край.",
    )

    portrait_focus_x = models.PositiveSmallIntegerField(
        "Фокус вертикального прев’ю по горизонталі",
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    portrait_focus_y = models.PositiveSmallIntegerField(
        "Фокус вертикального прев’ю по вертикалі",
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    is_published = models.BooleanField(
        "Показувати фото на сайті",
        default=False,
        help_text=(
            "Якщо вимкнено, фото зберігається в адмінці, "
            "але не відображається на сайті."
        ),
    )

    order = models.PositiveIntegerField(
        "Порядок відображення",
        default=0,
        help_text="Менше число — фото буде показане раніше.",
    )

    @property
    def responsive_image(self):
        manifest = self.image_variants or {}

        if (
            not self.image
            or manifest.get("source") != self.image.name
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
                    "url": self.image.storage.url(variant["name"]),
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

    @property
    def display_alt(self):
        """Alt для <img>: опис → підпис → назва категорії (ніколи не порожній)."""
        return (
            (self.alt_text or "").strip()
            or (self.caption or "").strip()
            or str(self.get_category_display())
        )

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"Фото #{self.pk}"
