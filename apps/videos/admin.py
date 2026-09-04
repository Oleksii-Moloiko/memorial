from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString
from modeltranslation.admin import TranslationAdmin

from .models import Video


@admin.register(Video)
class VideoAdmin(TranslationAdmin):
    """Admin configuration for memorial videos."""

    list_display = (
        "thumbnail_preview",
        "title",
        "category",
        "recorded_at",
        "is_featured",
        "is_published",
        "order",
    )
    list_display_links = ("thumbnail_preview", "title")
    list_editable = ("is_featured", "is_published", "order")
    list_filter = ("category", "is_featured", "is_published", "created_at")
    search_fields = ("title", "description", "recorded_at", "transcript")
    readonly_fields = (
        "large_thumbnail_preview",
        "video_preview",
    )
    date_hierarchy = "created_at"
    ordering = ("order", "id")
    list_per_page = 30
    save_on_top = True
    fieldsets = (
        (
            "ВІДЕО",
            {
                "fields": (
                    "video_file",
                    "video_preview",
                    "thumbnail",
                    "large_thumbnail_preview",
                )
            },
        ),
        (
            "ОСНОВНА ІНФОРМАЦІЯ",
            {
                "fields": (
                    "title",
                    "description",
                )
            },
        ),
        (
            "КЛАСИФІКАЦІЯ",
            {
                "fields": (
                    "category",
                    "recorded_at",
                    "duration",
                )
            },
        ),
        (
            "ДОСТУПНІСТЬ",
            {"fields": ("transcript",)},
        ),
        (
            "ПУБЛІКАЦІЯ",
            {
                "fields": (
                    "is_featured",
                    "is_published",
                    "order",
                )
            },
        ),
    )

    @admin.display(description="Обкладинка")
    def thumbnail_preview(self, obj: Video) -> SafeString | str:
        """Render a compact thumbnail preview."""
        try:
            if not obj.thumbnail:
                return "—"
            return format_html(
                '<img src="{}" style="display:block;width:90px;max-width:100%;'
                'height:50px;object-fit:cover;border-radius:4px;">',
                obj.thumbnail.url,
            )
        except (ValueError, OSError):
            return "Файл недоступний"

    @admin.display(description="Перегляд обкладинки")
    def large_thumbnail_preview(self, obj: Video) -> SafeString | str:
        """Render a large thumbnail preview."""
        try:
            if not obj.pk or not obj.thumbnail:
                return "Обкладинку ще не додано."
            return format_html(
                '<img src="{}" style="display:block;width:100%;max-width:500px;'
                'height:auto;max-height:280px;object-fit:contain;">',
                obj.thumbnail.url,
            )
        except (ValueError, OSError):
            return "Не вдалося відкрити обкладинку."

    @admin.display(description="Перегляд відео")
    def video_preview(self, obj: Video) -> SafeString | str:
        """Render an HTML5 video player on the edit page."""
        try:
            if not obj.pk or not obj.video_file:
                return "Збережіть відео, щоб побачити перегляд."
            return format_html(
                '<video controls preload="metadata" '
                'style="display:block;width:100%;max-width:600px;height:auto;">'
                '<source src="{}">'
                "Ваш браузер не підтримує відео."
                "</video>",
                obj.video_file.url,
            )
        except (ValueError, OSError):
            return "Не вдалося відкрити відеофайл."
