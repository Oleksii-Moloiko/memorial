from django.contrib import admin
from django.http import HttpRequest

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for global singleton site settings."""

    fieldsets = (
        (
            "Брендинг",
            {
                "fields": (
                    "site_title",
                    "brand_letter",
                    "site_name",
                    "subtitle",
                )
            },
        ),
        (
            "Футер",
            {"fields": ("footer_text", "copyright_holder")},
        ),
        (
            "Службові налаштування",
            {"fields": ("demo_strip_enabled",)},
        ),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Allow only one site settings record."""
        return not SiteSettings.objects.exists()

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: SiteSettings | None = None,
    ) -> bool:
        """Prevent deletion of global settings."""
        return False
