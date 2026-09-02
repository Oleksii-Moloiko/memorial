from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect
from apps.media_mentions.models import MediaMention

from .models import (
    ServicePage,
    ServiceAward,
    ServiceQuote,
)

class ServiceAwardInline(admin.StackedInline):
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


class ServiceQuoteInline(admin.StackedInline):
    model = ServiceQuote
    extra = 0
    fields = (
        "text",
        "context",
        "order",
    )


class MediaMentionInline(admin.StackedInline):
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
class ServicePageAdmin(admin.ModelAdmin):
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
            "2. ОПИС СЛУЖБИ",
            {
                "fields": (
                    "service_intro",
                    "service_text",
                    "editorial_note",
                )
            },
        ),
        (
            "3. НАГОРОДА",
            {
                "fields": (
                    "award_title",
                    "award_subtitle",
                    "decree_date",
                    "decree_number",
                    "decree_source_name",
                    "decree_url",
                )
            },
        ),
        (
            "4. ПУБЛІКАЦІЯ СТОРІНКИ",
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

