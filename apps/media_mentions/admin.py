from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString

from .models import MediaMention


@admin.register(MediaMention)
class MediaMentionAdmin(admin.ModelAdmin):
    """Admin configuration for external media mentions."""

    list_display = ("source_name", "published_date", "external_link", "order")
    list_editable = ("order",)
    list_filter = ("published_date",)
    search_fields = ("source_name", "url")
    date_hierarchy = "published_date"
    ordering = ("order", "-published_date")
    list_per_page = 30

    @admin.display(description="Посилання")
    def external_link(self, obj: MediaMention) -> SafeString | str:
        """Render a safe external link to the publication."""
        if not obj.url:
            return "—"
        return format_html(
            '<a href="{}" target="_blank" rel="noopener noreferrer">Відкрити</a>',
            obj.url,
        )
