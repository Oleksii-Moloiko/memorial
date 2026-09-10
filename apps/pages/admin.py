from django.contrib import admin
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.html import format_html

from apps.biography.models import Biography
from modeltranslation.admin import TranslationAdmin, TranslationStackedInline

from apps.media_mentions.models import MediaMention

from .models import (
    HomePage,
    LifePage,
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

@admin.register(HomePage)
class HomePageAdmin(
    ClientFriendlyAdminLabelsMixin,
    TranslationAdmin,
):
    readonly_fields = (
        "hero_content_link",
        "quote_content_link",
        "life_content_link",
        "gallery_content_link",
        "video_content_link",
        "links_content_link",
        "memories_content_link",
    )
    fieldsets = (
        (
            "1. ПЕРШИЙ ЕКРАН",
            {
                "fields": (
                    "hero_eyebrow",
                    "hero_primary_button_label",
                    "hero_secondary_button_label",
                    "hero_scroll_label",
                    "hero_content_link",
                )
            },
        ),
        (
            "ДОДАТКОВІ ТЕКСТИ ПЕРШОГО ЕКРАНУ",
            {
                "classes": ("collapse",),
                "description": (
                    "Ці тексти показуються, якщо основна "
                    "інформація про людину ще не заповнена."
                ),
                "fields": (
                    "hero_portrait_empty_label",
                    "empty_title",
                    "empty_text",
                ),
            },
        ),
        (
            "2. ЦИТАТА",
            {
                "fields": (
                    "quote_subtitle",
                    "quote_content_link",
                )
            },
        ),
        (
            "3. ЖИТТЯ",
            {
                "fields": (
                    "life_eyebrow",
                    "life_title",
                    "life_description",
                    "life_more_label",
                    "life_content_link",
                )
            },
        ),
        (
            "ДОДАТКОВІ ТЕКСТИ БЛОКУ «ЖИТТЯ»",
            {
                "classes": ("collapse",),
                "description": (
                    "Текст, який показується, якщо хронологію "
                    "ще не заповнено."
                ),
                "fields": (
                    "life_empty_text",
                ),
            },
        ),
        (
            "4. ФОТО",
            {
                "fields": (
                    "gallery_eyebrow",
                    "gallery_title",
                    "gallery_button_label",
                    "gallery_content_link",
                )
            },
        ),
        (
            "ДОДАТКОВІ ТЕКСТИ БЛОКУ «ФОТО»",
            {
                "classes": ("collapse",),
                "description": (
                    "Текст, який показується, якщо фотоархів "
                    "ще порожній."
                ),
                "fields": (
                    "gallery_empty_text",
                ),
            },
        ),
        (
            "5. ВІДЕО",
            {
                "fields": (
                    "video_eyebrow",
                    "video_button_label",
                    "video_content_link",
                )
            },
        ),
        (
            "ДОДАТКОВІ ТЕКСТИ БЛОКУ «ВІДЕО»",
            {
                "classes": ("collapse",),
                "description": (
                    "Ці тексти показуються, якщо рекомендоване "
                    "відео для головної сторінки не вибране."
                ),
                "fields": (
                    "video_empty_title",
                    "video_empty_description",
                ),
            },
        ),
        (
            "6. ПОСИЛАННЯ",
            {
                "fields": (
                    "links_eyebrow",
                    "links_source_button_label",
                    "links_archive_button_label",
                    "links_content_link",
                )
            },
        ),
        (
            "ДОДАТКОВІ ТЕКСТИ БЛОКУ «ПОСИЛАННЯ»",
            {
                "classes": ("collapse",),
                "description": (
                    "Ці тексти показуються, якщо рекомендоване "
                    "посилання для головної сторінки не вибране."
                ),
                "fields": (
                    "links_empty_title",
                    "links_empty_description",
                ),
            },
        ),
        (
            "7. СПОГАДИ",
            {
                "fields": (
                    "memories_eyebrow",
                    "memories_button_label",
                    "memories_content_link",
                )
            },
        ),
    )

    def _biography_url(self):
        biography = Biography.objects.first()

        if biography:
            return reverse(
                "admin:biography_biography_change",
                args=[biography.pk],
            )

        return reverse("admin:biography_biography_add")

    @admin.display(description="Основний контент першого екрану")
    def hero_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Редагувати портрет і основну інформацію"
            "</a>",
            self._biography_url(),
        )

    @admin.display(description="Головна цитата")
    def quote_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Редагувати головну цитату"
            "</a>",
            self._biography_url(),
        )

    @admin.display(description="Контент блоку життя")
    def life_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Керувати біографією та хронологією"
            "</a>",
            reverse("admin:pages_lifepage_changelist")
        )

    @admin.display(description="Фотографії")
    def gallery_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Керувати фото"
            "</a>",
            reverse("admin:gallery_photo_changelist"),
        )

    @admin.display(description="Відео")
    def video_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Керувати відео"
            "</a>",
            reverse("admin:videos_video_changelist"),
        )

    @admin.display(description="Матеріали та джерела")
    def links_content_link(self, obj):
        service_page = ServicePage.objects.first()

        if service_page:
            url = reverse(
                "admin:pages_servicepage_change",
                args=[service_page.pk],
            )
        else:
            url = reverse("admin:pages_servicepage_add")

        return format_html(
            '<a class="button" href="{}#mentions-group">'
            "Керувати посиланнями"
            "</a>",
            url,
        )

    @admin.display(description="Спогади")
    def memories_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Керувати спогадами"
            "</a>",
            reverse("admin:memories_memory_changelist"),
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not HomePage.objects.exists()

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: HomePage | None = None,
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
        page = HomePage.objects.first()

        if page:
            change_url = reverse(
                "admin:pages_homepage_change",
                args=[page.pk],
            )
            return HttpResponseRedirect(change_url)

        add_url = reverse("admin:pages_homepage_add")
        return HttpResponseRedirect(add_url)

@admin.register(LifePage)
class LifePageAdmin(
    ClientFriendlyAdminLabelsMixin,
    TranslationAdmin,
):
    readonly_fields = (
        "hero_content_link",
        "biography_content_link",
        "timeline_content_link",
        "photos_content_link",
    )

    fieldsets = (
        (
            "1. ПЕРШИЙ ЕКРАН",
            {
                "fields": (
                    "hero_eyebrow",
                    "hero_description",
                    "hero_content_link",
                )
            },
        ),
        (
            "2. БІОГРАФІЯ",
            {
                "fields": (
                    "birth_date_label",
                    "death_date_label",
                    "rank_label",
                    "award_label",
                    "principle_label",
                    "biography_content_link",
                )
            },
        ),
        (
            "3. ХРОНОЛОГІЯ",
            {
                "fields": (
                    "timeline_eyebrow",
                    "timeline_title",
                    "timeline_description",
                    "timeline_content_link",
                )
            },
        ),
        (
            "4. ФОТО ДО ІСТОРІЇ",
            {
                "fields": (
                    "photos_eyebrow",
                    "photos_title",

                    "childhood_photo",
                    "photos_childhood_label",

                    "study_photo",
                    "photos_study_label",

                    "family_photo",
                    "photos_family_label",

                    "photos_more_label",
                    "photos_archive_label",
                    "photos_content_link",
                )
            },
        ),
        (
            "ДОДАТКОВІ ТЕКСТИ",
            {
                "classes": ("collapse",),
                "description": (
                    "Рідко змінювані тексти, які показуються, "
                    "коли частина контенту ще не заповнена."
                ),
                "fields": (
                    "page_title_fallback",
                    "portrait_empty_label",
                    "empty_biography_text",
                    "empty_page_text",
                    "timeline_empty_title",
                    "timeline_empty_text",
                ),
            },
        ),
    )

    def _biography_url(self):
        biography = Biography.objects.first()

        if biography:
            return reverse(
                "admin:biography_biography_change",
                args=[biography.pk],
            )

        return reverse("admin:biography_biography_add")

    @admin.display(description="Основний контент першого екрану")
    def hero_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Редагувати портрет і основну інформацію"
            "</a>",
            self._biography_url(),
        )

    @admin.display(description="Біографічні дані")
    def biography_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Редагувати біографію"
            "</a>",
            self._biography_url(),
        )

    @admin.display(description="Події життя")
    def timeline_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Керувати хронологією"
            "</a>",
            reverse(
                "admin:biography_timelineevent_changelist"
            ),
        )

    @admin.display(description="Фотографії")
    def photos_content_link(self, obj):
        return format_html(
            '<a class="button" href="{}">'
            "Керувати фото"
            "</a>",
            reverse("admin:gallery_photo_changelist"),
        )

    def has_add_permission(self, request: HttpRequest) -> bool:
        return not LifePage.objects.exists()

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: LifePage | None = None,
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
        page = LifePage.objects.first()

        if page:
            return HttpResponseRedirect(
                reverse(
                    "admin:pages_lifepage_change",
                    args=[page.pk],
                )
            )

        return HttpResponseRedirect(
            reverse("admin:pages_lifepage_add")
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
