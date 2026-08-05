from django.contrib import admin

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fields = (
        "site_title",
        "brand_letter",
        "site_name",
        "subtitle",
        "footer_text",
        "copyright_holder",
        "demo_strip_enabled",
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
