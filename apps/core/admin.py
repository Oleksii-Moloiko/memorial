from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from modeltranslation.admin import TranslationAdmin

from apps.seo.models import SeoPage

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(TranslationAdmin):
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
                    "home_title",
                    "life_title",
                    "service_title",
                    "photos_title",
                    "videos_title",
                    "memories_title",
                )
            },
        ),
        (
            "СТОРІНКА «ПОДВИГ І СЛУЖБА»",
            {
                "fields": (
                    "service_section_title",
                    "service_award_title",
                    "service_safety_eyebrow",
                    "service_editorial_label",
                    "service_empty_text",
                    "service_decree_link_text",
                    "service_checklist_eyebrow",
                    "service_checklist_title",
                    "service_checklist_item_1",
                    "service_checklist_item_2",
                    "service_checklist_item_3",
                    "service_checklist_item_4",
                )
            },
        ),
        (
            "СТОРІНКА «СПОГАДИ»",
            {
                "fields": (
                    "memories_hero_eyebrow",
                    "memories_hero_description",
                    "memories_moderation_note",
                    "memories_empty_title",
                    "memories_empty_text",
                    "memories_submit_eyebrow",
                    "memories_submit_title",
                    "memories_submit_description",
                    "memories_submit_button_label",
                    "memories_success_message",
                    "memories_error_message",
                    "memories_rate_limit_message",
                    "memories_moderation_label",
                    "memories_moderator_text",
                )
            },
        ),
        (
            "ФУТЕР",
            {
                "fields": (
                    "footer_text",
                    "footer_dedication",
                    "copyright_holder",
                )
            },
        ),
        (
            "СПОГАДИ — ФОРМА ТА ДІАЛОГ",
            {
                "fields": (
                    "memories_name_label",
                    "memories_name_placeholder",
                    "memories_category_label",
                    "memories_category_placeholder",
                    "memories_text_label",
                    "memories_text_placeholder",
                    "memories_text_hint",
                    "memories_consent_label",
                    "memories_more_label",
                    "memories_limit_message",
                    "memories_name_error",
                    "memories_text_error",
                    "memories_required_error",
                    "memories_invalid_error",
                    "memories_close_label",
                    "memories_close_dialog_label",
                    "memories_characters_label",
                    "memories_escape_label",
                )
            },
        ),
        (
            "ПІДПИСИ І КАТЕГОРІЇ ФОТО ТА ВІДЕО",
            {
                "fields": (
                    "photos_all_label",
                    "videos_date_label",
                    "videos_category_label",
                    "videos_duration_label",
                    "photo_category_family",
                    "photo_category_study",
                    "photo_category_service",
                    "photo_category_memory",
                    "video_category_family",
                    "video_category_interview",
                    "video_category_service",
                    "video_category_memory",
                    "video_category_media",
                    "video_category_other",
                )
            },
        ),
        (
            "МОВА ТА ДЕМО",
            {
                "fields": (
                    "language_label",
                    "mobile_language_label",
                    "demo_title",
                    "demo_text",
                )
            },
        ),
        (
            "СЛУЖБОВІ НАЛАШТУВАННЯ",
            {"fields": ("demo_strip_enabled",)},
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
                        else (reverse("admin:seo_seopage_add") + f"?page_key={key}")
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
