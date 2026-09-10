from django.contrib import admin
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils.html import format_html
from django.utils.safestring import SafeString
from modeltranslation.admin import TranslationAdmin

from .models import Biography, TimelineEvent


@admin.register(Biography)
class BiographyAdmin(TranslationAdmin):
    """Admin configuration for the memorial biography."""

    list_display = (
        "portrait_preview",
        "full_name",
        "rank",
        "birth_date",
        "death_date",
    )
    search_fields = ("full_name", "rank", "award_title")
    readonly_fields = ("large_portrait_preview",)
    fieldsets = (
        (
            "ГОЛОВНА — ПЕРШИЙ ЕКРАН",
            {
                "description": (
                    "Поля цього блоку відображаються у першому екрані "
                    "головної сторінки."
                ),
                "fields": (
                    "portrait",
                    "large_portrait_preview",
                    "full_name",
                    "rank",
                    "birth_date",
                    "death_date",
                    "award_title",
                    "intro_text",
                ),
            },
        ),
        (
            "ГОЛОВНА — ЦИТАТА",
            {
                "description": "Окремий блок-цитата під першим екраном.",
                "fields": ("signature_quote",),
            },
        ),
        (
            "ЖИТТЯ — БІОГРАФІЯ",
            {
                "description": (
                    "Тексти основного біографічного блоку на сторінці «Життя»."
                ),
                "fields": (
                    "summary",
                    "full_text",
                ),
            },
        ),
    )

    def response_change(self, request, obj):
        if "_continue" in request.POST:
            return super().response_change(request, obj)

        return redirect("admin:pages_lifepage_changelist")

    def response_add(
            self,
            request,
            obj,
            post_url_continue=None,
    ):
        if "_continue" in request.POST:
            return super().response_add(
                request,
                obj,
                post_url_continue=post_url_continue,
            )

        return redirect("admin:pages_lifepage_changelist")

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Allow only one biography record."""
        return not Biography.objects.exists()

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Biography | None = None,
    ) -> bool:
        """Protect the singleton biography from accidental deletion."""
        return False

    @admin.display(description="Портрет")
    def portrait_preview(self, obj: Biography) -> SafeString | str:
        """Render a compact portrait preview in the list page."""
        try:
            if not obj.portrait:
                return "—"
            return format_html(
                '<img src="{}" style="width:52px;height:52px;'
                'object-fit:cover;border-radius:50%;">',
                obj.portrait.url,
            )
        except (ValueError, OSError):
            return "Файл недоступний"

    @admin.display(description="Перегляд портрета")
    def large_portrait_preview(self, obj: Biography) -> SafeString | str:
        """Render a large portrait preview on the edit page."""
        try:
            if not obj.pk or not obj.portrait:
                return "Портрет ще не додано."
            return format_html(
                '<img src="{}" style="max-width:360px;max-height:420px;'
                'object-fit:contain;border-radius:8px;">',
                obj.portrait.url,
            )
        except (ValueError, OSError):
            return "Не вдалося відкрити файл портрета."


@admin.register(TimelineEvent)
class TimelineEventAdmin(TranslationAdmin):
    """Admin configuration for biography timeline events."""

    list_display = (
        "date_label",
        "title",
        "short_description",
        "order",
    )
    list_editable = ("order",)
    search_fields = (
        "date_label",
        "title",
        "description",
    )
    ordering = ("order", "id")
    list_per_page = 30

    def get_model_perms(self, request: HttpRequest) -> dict[str, bool]:
        """
        Hide TimelineEvent from the standard admin navigation.

        CRUD URLs remain available.
        """
        return {}

    def response_add(self, request, obj, post_url_continue=None):
        if "_continue" in request.POST:
            return super().response_add(
                request,
                obj,
                post_url_continue=post_url_continue,
            )

        return redirect("admin:pages_lifepage_changelist")

    def response_change(self, request, obj):
        if "_continue" in request.POST:
            return super().response_change(request, obj)

        return redirect("admin:pages_lifepage_changelist")

    def response_delete(self, request, obj_display, obj_id):
        return redirect("admin:pages_lifepage_changelist")

    @admin.display(description="Опис")
    def short_description(self, obj: TimelineEvent) -> str:
        if not obj.description:
            return "—"

        return (
            f"{obj.description[:80]}…" if len(obj.description) > 80 else obj.description
        )
