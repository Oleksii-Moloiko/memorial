from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString

from .models import Photo


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    """Admin configuration for memorial gallery photos."""

    list_display = (
        "preview",
        "caption",
        "category",
        "layout_size",
        "is_published",
        "order",
    )
    list_display_links = ("preview", "caption")
    list_editable = ("is_published", "order")
    list_filter = ("category", "is_published", "layout_size")
    search_fields = ("caption", "alt_text")
    readonly_fields = ("large_preview",)
    ordering = ("order", "id")
    list_per_page = 30
    save_on_top = True
    fieldsets = (
        (
            "Зображення",
            {
                "fields": (
                    "image",
                    "large_preview",
                    "caption",
                    "alt_text",
                )
            },
        ),
        (
            "Відображення",
            {
                "fields": (
                    "category",
                    "layout_size",
                    "is_published",
                    "order",
                )
            },
        ),
    )

    @admin.display(description="Прев’ю")
    def preview(self, obj: Photo) -> SafeString | str:
        """Render a compact photo preview."""
        try:
            if not obj.image:
                return "—"
            return format_html(
                '<img src="{}" style="width:70px;height:50px;'
                'object-fit:cover;border-radius:4px;">',
                obj.image.url,
            )
        except (ValueError, OSError):
            return "Файл недоступний"

    @admin.display(description="Перегляд")
    def large_preview(self, obj: Photo) -> SafeString | str:
        """Render a large photo preview on the edit page."""
        try:
            if not obj.pk or not obj.image:
                return "Збережіть фото, щоб побачити прев’ю."
            return format_html(
                '<img src="{}" style="max-width:500px;max-height:350px;'
                'object-fit:contain;">',
                obj.image.url,
            )
        except (ValueError, OSError):
            return "Не вдалося відкрити файл зображення."
