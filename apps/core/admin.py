from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from apps.seo.models import SeoPage

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for global singleton site settings."""
    change_form_template = "admin/core/sitesettings/change_form.html"

    fieldsets = (
        (
            "ЗАГАЛЬНІ",
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
            "НАЗВИ РОЗДІЛІВ",
            {
                "fields": (
                    "biography_title",
                    "memories_title",
                    "publications_title",
                    "gallery_title",
                )
            },
        ),
        (
            "ФУТЕР",
            {
                "fields": (
                    "footer_text",
                    "copyright_holder",
                )
            },
        ),
        (
            "СЛУЖБОВІ НАЛАШТУВАННЯ",
            {
                "fields": (
                    "demo_strip_enabled",
                )
            },
        ),
    )

    def change_view(
            self,
            request,
            object_id,
            form_url="",
            extra_context=None,
    ):
        extra_context = extra_context or {}

        seo_pages = []

        for key, label in SeoPage.PageKey.choices:
            seo_page = SeoPage.objects.filter(
                page_key=key,
            ).first()

            seo_pages.append(
                {
                    "key": key,
                    "label": label,
                    "object": seo_page,
                    "url": (
                        reverse(
                            "admin:seo_seopage_change",
                            args=[seo_page.pk],
                        )
                        if seo_page
                        else (
                                reverse("admin:seo_seopage_add")
                                + f"?page_key={key}"
                        )
                    ),
                }
            )

        extra_context["seo_pages"] = seo_pages

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    def changelist_view(
            self,
            request: HttpRequest,
            extra_context=None,
    ):
        settings = SiteSettings.load()

        change_url = reverse(
            "admin:core_sitesettings_change",
            args=[settings.pk],
        )

        return HttpResponseRedirect(change_url)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Allow only one site settings record."""
        return not SiteSettings.objects.exists()

    def response_change(self, request, obj):
        if "_continue" in request.POST:
            return super().response_change(request, obj)

        return redirect("admin:index")

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: SiteSettings | None = None,
    ) -> bool:
        """Prevent deletion of global settings."""
        return False
