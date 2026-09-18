import uuid
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.fields.files import FieldFile

from .storage import get_video_storage


VIDEO_ALLOWED_EXTENSIONS = {".mp4", ".webm", ".mov"}
VIDEO_MAX_SIZE = 300 * 1024 * 1024  # 300 MB


def validate_video_extension(file):
    extension = Path(file.name).suffix.lower()

    if extension not in VIDEO_ALLOWED_EXTENSIONS:
        raise ValidationError("Дозволені формати відео: MP4, WebM або MOV.")


def validate_video_size(file):
    # Уже збережені файли повторно не перевіряємо через storage.
    # Direct upload перевіряється через HEAD у confirm_video_upload().
    if isinstance(file, FieldFile) and file._committed:
        return

    if file.size > VIDEO_MAX_SIZE:
        raise ValidationError(
            "Розмір відео не повинен перевищувати 300 MB."
        )

class VideoUpload(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Очікує завантаження"
        VERIFIED = "verified", "Завантажено та перевірено"
        ATTACHED = "attached", "Прив’язано до відео"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="video_uploads",
    )

    object_key = models.CharField(
        max_length=500,
        unique=True,
    )

    original_name = models.CharField(
        max_length=255,
    )

    content_type = models.CharField(
        max_length=100,
        blank=True,
    )

    declared_size = models.PositiveBigIntegerField()

    actual_size = models.PositiveBigIntegerField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    attached_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.original_name} ({self.status})"

class Video(models.Model):
    class Category(models.TextChoices):
        FAMILY = "family", _("Сімейний архів")
        INTERVIEW = "interview", _("Інтерв’ю")
        SERVICE = "service", _("Служба")
        MEMORY = "memory", _("Вшанування")
        MEDIA = "media", _("Матеріали ЗМІ")
        OTHER = "other", _("Інше")

    title = models.CharField(
        "Назва",
        max_length=255,
    )

    video_file = models.FileField(
        "Відеофайл",
        upload_to="videos/files/",
        storage=get_video_storage,
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
        help_text=(
            "Допомагає класифікувати відео та показує його тип "
            "у відповідних блоках сайту."
        ),
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
        "Показувати як рекомендоване",
        default=False,
        help_text=(
            "Рекомендованим може бути лише одне відео. "
            "Якщо вибрати інше, попереднє перестане бути рекомендованим."
        ),
    )

    is_published = models.BooleanField(
        "Показувати відео на сайті",
        default=False,
        help_text=(
            "Якщо вимкнено, відео зберігається в адмінці, "
            "але не відображається на сайті."
        ),
    )

    order = models.PositiveIntegerField(
        "Порядок відображення",
        default=0,
        help_text="Менше число — відео буде показане раніше.",
    )

    created_at = models.DateTimeField(
        "Додано",
        auto_now_add=True,
    )

    def save(self, *args, **kwargs):
        if not self.is_published:
            self.is_featured = False
        elif self.is_featured:
            Video.objects.exclude(pk=self.pk).filter(
                is_featured=True,
            ).update(is_featured=False)

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Відео"
        verbose_name_plural = "Відео"
        ordering = ["order", "id"]

    def __str__(self):
        return self.title
