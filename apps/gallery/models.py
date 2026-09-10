from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Photo(models.Model):
    class Category(models.TextChoices):
        FAMILY = "family", "Сім’я та дитинство"
        STUDY = "study", "Навчання"
        SERVICE = "service", "Служба та побратими"
        MEMORY = "memory", "Вшанування"

    class LayoutSize(models.TextChoices):
        NORMAL = "", "Автоматично"
        TALL = "span-tall", "Вертикальне 9:16"
        WIDE = "span-wide", "Горизонтальне 16:9"

    image = models.ImageField(
        "Фото",
        upload_to="gallery/",
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
        help_text=(
            "Визначає, у якій категорії фото буде показане "
            "на сторінці."
        ),
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

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"Фото #{self.pk}"
