from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect

from .models import ServicePage


@admin.register(ServicePage)
class ServicePageAdmin(admin.ModelAdmin):
    list_display = (
        "hero_title",
        "publication_status",
        "is_published",
    )
    readonly_fields = ("updated_at",)

    fieldsets = (
        (
            "ПЕРШИЙ ЕКРАН",
            {
                "fields": (
                    "hero_eyebrow",
                    "hero_title",
                    "hero_description",
                )
            },
        ),
        (
            "СЛУЖБА",
            {
                "fields": (
                    "service_intro",
                    "service_text",
                    "editorial_note",
                )
            },
        ),
        (
            "НАГОРОДА",
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
            "ПУБЛІКАЦІЯ",
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