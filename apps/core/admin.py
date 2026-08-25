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
                    "home_title",
                    "life_title",
                    "service_title",
                    "photos_title",
                    "videos_title",
                    "media_title",
                    "memories_title",
                )
            },
        ),
        (
            "ГОЛОВНА СТОРІНКА",
            {
                "fields": (
                    "home_hero_eyebrow",
                    "home_empty_title",
                    "home_empty_text",

                    "home_life_eyebrow",
                    "home_life_title",
                    "home_life_description",
                    "home_life_empty_text",

                    "home_gallery_eyebrow",
                    "home_gallery_title",
                    "home_gallery_empty_text",

                    "home_video_title",
                    "home_video_description",

                    "home_media_eyebrow",
                    "home_media_title",
                    "home_media_description",
                )
            },
        ),
        (
            "СТОРІНКА «ЖИТТЯ»",
            {
                "fields": (
                    "life_hero_eyebrow",
                    "life_hero_description",
                    "life_empty_biography_text",
                    "life_empty_page_text",

                    "life_timeline_eyebrow",
                    "life_timeline_title",
                    "life_timeline_description",
                    "life_timeline_empty_title",
                    "life_timeline_empty_text",

                    "life_photos_eyebrow",
                    "life_photos_title",
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
            "СТОРІНКА «ФОТО»",
            {
                "fields": (
                    "photos_hero_title",
                    "photos_hero_description",
                    "photos_verification_note",
                    "photos_category_empty_text",
                    "photos_empty_title",
                    "photos_empty_text",
                )
            },
        ),
        (
            "СТОРІНКА «ВІДЕО»",
            {
                "fields": (
                    "videos_hero_eyebrow",
                    "videos_hero_description",
                    "videos_featured_label",
                    "videos_transcript_label",

                    "videos_all_records_label",
                    "videos_archive_title",
                    "videos_admin_note",

                    "videos_empty_title",
                    "videos_empty_text",

                    "videos_accessibility_label",
                    "videos_accessibility_text",
                )
            },
        ),
        (
            "СТОРІНКА «МАТЕРІАЛИ»",
            {
                "fields": (
                    "media_hero_eyebrow",
                    "media_hero_description",
                    "media_section_title",
                    "media_verification_note",
                    "media_empty_title",
                    "media_empty_text",
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
