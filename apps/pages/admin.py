from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.urls import reverse

from .models import ServicePage


@admin.register(ServicePage)
class ServicePageAdmin(admin.ModelAdmin):
    list_display = (
        "hero_title",
        "publication_status",
        "is_published",
        "updated_at",
    )
    readonly_fields = ("updated_at",)

    fieldsets = (
        (
            "Перший екран",
            {
                "fields": (
                    "hero_eyebrow",
                    "hero_title",
                    "hero_description",
                    "publication_status",
                )
            },
        ),
        (
            "Опис служби",
            {
                "fields": (
                    "service_intro",
                    "service_text",
                    "editorial_note",
                )
            },
        ),
        (
            "Нагорода",
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
            "Публікація",
            {
                "fields": (
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