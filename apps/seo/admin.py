from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse
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

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)

        if obj is not None:
            return tuple(
                (name, options)
                for name, options in fieldsets
                if "page_key" not in options.get("fields", ())
            )

        return fieldsets

    def response_add(self, request, obj, post_url_continue=None):
        response = super().response_add(
            request,
            obj,
            post_url_continue=post_url_continue,
        )

        if "_save" in request.POST and "_popup" not in request.POST:
            return redirect(
                reverse("admin:seo_seopage_change", args=[obj.pk])
            )

        return response

    def response_change(self, request, obj):
        response = super().response_change(request, obj)

        if "_save" in request.POST and "_popup" not in request.POST:
            return redirect(
                reverse("admin:seo_seopage_change", args=[obj.pk])
            )

        return response



    def changeform_view(
        self,
        request,
        object_id=None,
        form_url="",
        extra_context=None,
    ):
        extra_context = {
            **(extra_context or {}),
            "show_save_and_add_another": False,
        }

        return super().changeform_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )



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
