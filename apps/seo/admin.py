from django.contrib import admin
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils.safestring import SafeString
from modeltranslation.admin import TranslationAdmin

from .models import SeoPage


@admin.register(SeoPage)
class SeoPageAdmin(TranslationAdmin):
    """Admin configuration for page SEO metadata."""

    list_display = ("page_key", "title", "description_length", "image_preview")
    list_filter = ("page_key",)
    search_fields = ("title", "description")
    readonly_fields = ("large_image_preview",)
    ordering = ("page_key",)
    fieldsets = (
        (
            "Сторінка",
            {"fields": ("page_key",)},
        ),
        (
            "Метадані",
            {"fields": ("title", "description")},
        ),
        (
            "Open Graph",
            {"fields": ("og_image", "large_image_preview")},
        ),
    )

    def response_add(self, request, obj, post_url_continue=None):
        if "_continue" in request.POST:
            return super().response_add(
                request,
                obj,
                post_url_continue=post_url_continue,
            )

        return redirect("admin:core_sitesettings_changelist")

    def response_change(self, request, obj):
        if "_continue" in request.POST:
            return super().response_change(request, obj)

        return redirect("admin:core_sitesettings_changelist")

    def response_delete(self, request, obj_display, obj_id):
        return redirect("admin:core_sitesettings_changelist")

    def get_model_perms(self, request):
        return {}

    @admin.display(description="Символів в описі")
    def description_length(self, obj: SeoPage) -> int:
        """Return the current meta description length."""
        return len(obj.description)

    @admin.display(description="OG-зображення")
    def image_preview(self, obj: SeoPage) -> SafeString | str:
        """Render a compact Open Graph image preview."""
        try:
            if not obj.og_image:
                return "—"
            return format_html(
                '<img src="{}" style="width:80px;height:45px;'
                'object-fit:cover;border-radius:4px;">',
                obj.og_image.url,
            )
        except (ValueError, OSError):
            return "Файл недоступний"

    @admin.display(description="Перегляд OG-зображення")
    def large_image_preview(self, obj: SeoPage) -> SafeString | str:
        """Render a large Open Graph image preview."""
        try:
            if not obj.pk or not obj.og_image:
                return "OG-зображення ще не додано."
            return format_html(
                '<img src="{}" style="max-width:500px;max-height:280px;'
                'object-fit:contain;">',
                obj.og_image.url,
            )
        except (ValueError, OSError):
            return "Не вдалося відкрити OG-зображення."
