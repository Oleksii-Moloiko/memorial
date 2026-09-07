from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline

from apps.media_mentions.models import MediaMention

from .models import (
    ServiceAward,
    ServicePage,
    ServiceQuote,
)


class ServiceAwardInline(TranslationStackedInline):
    model = ServiceAward
    extra = 0
    fields = (
        "title",
        "subtitle",
        "decree_date",
        "decree_number",
        "decree_source_name",
        "decree_url",
        "order",
    )


class ServiceQuoteInline(TranslationStackedInline):
    model = ServiceQuote
    extra = 0
    fields = (
        "text",
        "context",
        "order",
    )


class MediaMentionInline(TranslationStackedInline):
    model = MediaMention
    extra = 0
    fields = (
        "title",
        "source_name",
        "category",
        "published_date",
        "url",
        "is_published",
        "is_featured",
        "order",
    )


@admin.register(ServicePage)
class ServicePageAdmin(TranslationAdmin):
    inlines = [
        ServiceAwardInline,
        ServiceQuoteInline,
        MediaMentionInline,
    ]
    list_display = (
        "hero_title",
        "publication_status",
        "is_published",
    )
    readonly_fields = ("updated_at",)

    fieldsets = (
        (
            "1. ПЕРШИЙ ЕКРАН",
            {
                "fields": (
                    "hero_eyebrow",
                    "hero_title",
                    "hero_description",
                )
            },
        ),
        (
            "2. НАВІГАЦІЯ ПО СТОРІНЦІ",
            {
                "fields": (
                    "index_eyebrow",
                )
            },
        ),
        (
            "3. ТЕКСТИ БЛОКУ «НАГОРОДИ»",
            {
                "fields": (
                    "awards_eyebrow",
                    "awards_title",
                    "award_date_label",
                    "award_number_label",
                    "award_source_label",
                )
            },
        ),
        (
            "4. ТЕКСТИ БЛОКУ «ЦИТАТИ»",
            {
                "fields": (
                    "quotes_eyebrow",
                    "quotes_title",
                    "quote_more_label",
                )
            },
        ),
        (
            "5. ТЕКСТИ БЛОКУ «ПОСИЛАННЯ»",
            {
                "fields": (
                    "links_nav_label",
                    "links_eyebrow",
                    "links_title",
                    "links_description",
                    "links_verification_note",
                    "links_empty_title",
                    "links_empty_text",
                    "links_missing_date_label",
                )
            },
        ),
        (
            "6. ПУБЛІКАЦІЯ СТОРІНКИ",
            {
                "fields": (
                    "publication_status",
                    "is_published",
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not ServicePage.objects.exists()

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: ServicePage | None = None,
    ) -> bool:
        return False

    def response_add(self, request, obj, post_url_continue=None):
        if "_continue" in request.POST:
            return super().response_add(
                request,
                obj,
                post_url_continue=post_url_continue,
            )

        return redirect("admin:index")

    def response_change(self, request, obj):
        if "_continue" in request.POST:
            return super().response_change(request, obj)

        return redirect("admin:index")

    def changelist_view(
        self,
        request: HttpRequest,
        extra_context=None,
    ):
        page = ServicePage.objects.first()

        if page:
            change_url = reverse(
                "admin:pages_servicepage_change",
                args=[page.pk],
            )
            return HttpResponseRedirect(change_url)

        add_url = reverse("admin:pages_servicepage_add")
        return HttpResponseRedirect(add_url)
