from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Admin configuration for memorial videos."""

    list_display = (
        "thumbnail_preview",
        "title",
        "category",
        "recorded_at",
        "duration",
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
        "created_at",
    )
    date_hierarchy = "created_at"
    ordering = ("order", "id")
    list_per_page = 30
    save_on_top = True
    fieldsets = (
        (
            "Основна інформація",
            {
                "fields": (
                    "title",
                    "description",
                    "category",
                    "recorded_at",
                    "duration",
                )
            },
        ),
        (
            "Файли",
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
            "Доступність",
            {"fields": ("transcript",)},
        ),
        (
            "Публікація",
            {
                "fields": (
                    "is_featured",
                    "is_published",
                    "order",
                    "created_at",
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
                '<img src="{}" style="width:90px;height:50px;'
                'object-fit:cover;border-radius:4px;">',
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
                '<img src="{}" style="max-width:500px;max-height:280px;'
                'object-fit:contain;">',
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
                'style="max-width:600px;width:100%;">'
                '<source src="{}">'
                "Ваш браузер не підтримує відео."
                "</video>",
                obj.video_file.url,
            )
        except (ValueError, OSError):
            return "Не вдалося відкрити відеофайл."
