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

class ClientFriendlyAdminLabelsMixin:
    """Прибирає технічні позначки мов і пояснює службові поля."""

    client_field_labels = {}
    client_field_help_texts = {}

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(
            db_field,
            request,
            **kwargs,
        )

        if formfield is None:
            return None

        field_name = db_field.name
        base_field_name = field_name

        for language in ("uk", "en"):
            suffix = f"_{language}"

            if field_name.endswith(suffix):
                base_field_name = field_name.removesuffix(suffix)

                if formfield.label:
                    label_suffix = f" [{language}]"

                    if formfield.label.endswith(label_suffix):
                        formfield.label = formfield.label.removesuffix(
                            label_suffix
                        )

                break

        if base_field_name == "order":
            formfield.label = "Порядок відображення"
            formfield.help_text = (
                "Менше число — елемент буде показаний вище."
            )

        if base_field_name in self.client_field_labels:
            formfield.label = self.client_field_labels[
                base_field_name
            ]

        if base_field_name in self.client_field_help_texts:
            formfield.help_text = self.client_field_help_texts[
                base_field_name
            ]

        return formfield


class ServiceAwardInline(
    ClientFriendlyAdminLabelsMixin,
    TranslationStackedInline,
):
    model = ServiceAward
    extra = 0
    verbose_name = "нагорода"
    verbose_name_plural = "Список нагород"
    client_field_labels = {
        "subtitle": "Уточнення до нагороди",
        "decree_source_name": "Офіційне джерело",
    }

    client_field_help_texts = {
        "subtitle": (
            "Наприклад: «II ступеня» або «посмертно»."
        ),
        "decree_source_name": (
            "Назва установи або сайту, де опубліковано указ."
        ),
        "decree_url": (
            "Повне посилання на офіційний текст указу."
        ),
    }
    fields = (
        "title",
        "subtitle",
        "decree_date",
        "decree_number",
        "decree_source_name",
        "decree_url",
        "order",
    )


class ServiceQuoteInline(
    ClientFriendlyAdminLabelsMixin,
    TranslationStackedInline,
):
    model = ServiceQuote
    extra = 0
    verbose_name = "цитата"
    verbose_name_plural = "Список цитат"
    client_field_labels = {
        "text": "Текст цитати",
        "context": "Підпис / контекст",
    }

    client_field_help_texts = {
        "context": (
            "Наприклад: «із розмови з побратимами»."
        ),
    }
    fields = (
        "text",
        "context",
        "order",
    )


class MediaMentionInline(
    ClientFriendlyAdminLabelsMixin,
    TranslationStackedInline,
):
    model = MediaMention
    extra = 0
    verbose_name = "посилання"
    verbose_name_plural = "Список посилань"
    client_field_labels = {
        "title": "Назва матеріалу",
        "category": "Тип джерела",
        "url": "Посилання на матеріал",
        "is_published": "Показувати посилання на сайті",
        "is_featured": (
            "Показувати посилання на головній сторінці"
        ),
    }

    client_field_help_texts = {
        "published_date": (
            "Якщо дата невідома, залиште поле порожнім."
        ),
        "is_featured": (
            "На головній сторінці може бути лише одне "
            "посилання. Якщо вибрати інше, попереднє "
            "буде знято автоматично."
        ),
    }

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
class ServicePageAdmin(
    ClientFriendlyAdminLabelsMixin,
    TranslationAdmin,
):
    change_form_template = "admin/pages/servicepage/change_form.html"
    client_field_labels = {
        "publication_status": "Стан погодження",
        "is_published": "Показувати сторінку на сайті",
    }

    client_field_help_texts = {
        "publication_status": (
            "Внутрішній статус матеріалів перед публікацією."
        ),
        "is_published": (
            "Увімкніть, коли сторінка готова до показу відвідувачам."
        ),
    }
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
            "3. НАГОРОДИ",
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
            "4. ЦИТАТИ",
            {
                "fields": (
                    "quotes_eyebrow",
                    "quotes_title",
                    "quote_more_label",
                )
            },
        ),
        (
            "5. ПОСИЛАННЯ",
            {
                "fields": (
                    "links_nav_label",
                    "links_eyebrow",
                    "links_title",
                    "links_description",
                )
            },
        ),
        (
            "ДОДАТКОВІ ТЕКСТИ ПОСИЛАНЬ",
            {
                "classes": ("collapse",),
                "description": (
                    "Рідко змінювані тексти для перевірки посилань, "
                    "порожнього стану та відсутньої дати."
                ),
                "fields": (
                    "links_verification_note",
                    "links_empty_title",
                    "links_empty_text",
                    "links_missing_date_label",
                ),
            },
        ),
        (
            "6. ПУБЛІКАЦІЯ",
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
