from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString

from .models import MediaMention


@admin.register(MediaMention)
class MediaMentionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "source_name",
        "category",
        "published_date",
        "is_featured",
        "is_published",
        "external_link",
        "order",
    )
    list_editable = (
        "is_featured",
        "is_published",
        "order",
    )
    list_filter = (
        "category",
        "is_featured",
        "is_published",
        "published_date",
    )
    search_fields = (
        "title",
        "source_name",
        "url",
    )
    date_hierarchy = "published_date"
    ordering = (
        "order",
        "-published_date",
    )
    list_per_page = 30

    fieldsets = (
        (
            "Матеріал",
            {
                "fields": (
                    "title",
                    "source_name",
                    "category",
                    "url",
                    "published_date",
                )
            },
        ),
        (
            "Публікація",
            {
                "fields": (
                    "is_featured",
                    "is_published",
                    "order",
                )
            },
        ),
    )

    @admin.display(description="Посилання")
    def external_link(
        self,
        obj: MediaMention,
    ) -> SafeString | str:
        if not obj.url:
            return "—"

        return format_html(
            '<a href="{}" target="_blank" '
            'rel="noopener noreferrer">Відкрити</a>',
            obj.url,
        )