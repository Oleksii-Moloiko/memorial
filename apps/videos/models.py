from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models


def validate_video_extension(file):
    allowed_extensions = {".mp4", ".webm", ".mov"}
    extension = Path(file.name).suffix.lower()

    if extension not in allowed_extensions:
        raise ValidationError("Дозволені формати відео: MP4, WebM або MOV.")


def validate_video_size(file):
    max_size = 300 * 1024 * 1024  # 300 MB

    if file.size > max_size:
        raise ValidationError("Розмір відео не повинен перевищувати 300 MB.")


class Video(models.Model):
    class Category(models.TextChoices):
        FAMILY = "family", "Сімейний архів"
        INTERVIEW = "interview", "Інтерв’ю"
        SERVICE = "service", "Служба"
        MEMORY = "memory", "Вшанування"
        MEDIA = "media", "Матеріали ЗМІ"
        OTHER = "other", "Інше"

    title = models.CharField(
        "Назва",
        max_length=255,
    )

    video_file = models.FileField(
        "Відеофайл",
        upload_to="videos/files/",
        validators=[
            validate_video_extension,
            validate_video_size,
        ],
        help_text=(
            "Дозволені формати: MP4, WebM або MOV. Максимальний розмір — 300 MB."
        ),
    )

    thumbnail = models.ImageField(
        "Обкладинка",
        upload_to="videos/thumbnails/",
        blank=True,
        null=True,
        help_text=("Рекомендоване співвідношення сторін — 16:9."),
    )

    description = models.TextField(
        "Короткий опис",
        blank=True,
        max_length=1000,
    )

    category = models.CharField(
        "Категорія",
        max_length=20,
        choices=Category.choices,
        default=Category.OTHER,
    )

    recorded_at = models.CharField(
        "Дата або період запису",
        max_length=100,
        blank=True,
        help_text="Наприклад: 2022 або листопад 2023.",
    )

    duration = models.CharField(
        "Тривалість",
        max_length=20,
        blank=True,
        help_text="Наприклад: 03:42.",
    )

    transcript = models.TextField(
        "Розшифровка або субтитри",
        blank=True,
        help_text=("Необов’язковий текстовий опис змісту відео."),
    )

    is_featured = models.BooleanField(
        "Рекомендоване відео",
        default=False,
        help_text=("На сторінці бажано мати лише одне рекомендоване відео."),
    )

    is_published = models.BooleanField(
        "Опубліковано",
        default=False,
        help_text=("Неопубліковане відео не відображається на сайті."),
    )

    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )

    created_at = models.DateTimeField(
        "Додано",
        auto_now_add=True,
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_featured:
            Video.objects.exclude(pk=self.pk).filter(
                is_featured=True,
            ).update(is_featured=False)

    class Meta:
        verbose_name = "Відео"
        verbose_name_plural = "Відео"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title
