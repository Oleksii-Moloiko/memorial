from django.db import models


class Photo(models.Model):
    class Category(models.TextChoices):
        FAMILY = "family", "Сім’я та дитинство"
        STUDY = "study", "Навчання"
        SERVICE = "service", "Служба та побратими"
        MEMORY = "memory", "Вшанування"

    class LayoutSize(models.TextChoices):
        NORMAL = "", "Звичайний"
        TALL = "span-tall", "Високий"
        WIDE = "span-wide", "Широкий"

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
    )

    layout_size = models.CharField(
        "Розмір у сітці",
        max_length=20,
        choices=LayoutSize.choices,
        blank=True,
    )

    is_published = models.BooleanField(
        "Опубліковано",
        default=False,
        help_text="Неопубліковане фото не відображається на сайті.",
    )

    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фотогалерея"
        ordering = ["order", "id"]

    def __str__(self):
        return self.caption or f"Фото #{self.pk}"
