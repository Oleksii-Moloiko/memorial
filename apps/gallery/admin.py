from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import SafeString
from modeltranslation.admin import TranslationAdmin

from .models import Photo


@admin.register(Photo)
class PhotoAdmin(TranslationAdmin):
    """Admin configuration for memorial gallery photos."""

    change_list_template = "admin/gallery/photo/change_list.html"

    list_display = (
        "preview",
        "caption",
        "category",
        "layout_size",
        "is_published",
        "order",
    )
    list_display_links = ("preview", "caption")
    list_editable = ("is_published", "order")
    list_filter = ("category", "is_published", "layout_size")
    search_fields = ("caption", "alt_text")
    readonly_fields = ("preview_crop_editor", "large_preview")
    ordering = ("order", "id")
    list_per_page = 30
    save_on_top = True
    fieldsets = (
        (
            "ФОТО",
            {
                "fields": (
                    "image",
                    "preview_crop_editor",
                    "preview_focus_x",
                    "preview_focus_y",
                    "large_preview",
                    "caption",
                    "alt_text",
                )
            },
        ),
        (
            "ВІДОБРАЖЕННЯ",
            {
                "fields": (
                    "category",
                    "layout_size",
                    "order",
                )
            },
        ),
        (
            "ПУБЛІКАЦІЯ",
            {"fields": ("is_published",)},
        ),
    )

    class Media:
        css = {"all": ("admin/css/photo_cropper.css",)}
        js = ("admin/js/photo_cropper.js",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(
            db_field,
            request,
            **kwargs,
        )

        if (
            formfield is not None
            and db_field.name in {"preview_focus_x", "preview_focus_y"}
        ):
            formfield.widget = forms.HiddenInput()

        return formfield

    @admin.display(description="Прев’ю")
    def preview(self, obj: Photo) -> SafeString | str:
        """Render a compact photo preview using the saved focal point."""
        try:
            if not obj.image:
                return "—"
            return format_html(
                '<img src="{}" style="width:70px;height:50px;'
                'object-fit:cover;object-position:{}% {}%;border-radius:4px;">',
                obj.image.url,
                obj.preview_focus_x,
                obj.preview_focus_y,
            )
        except (ValueError, OSError):
            return "Файл недоступний"

    @admin.display(description="Область прев’ю")
    def preview_crop_editor(self, obj: Photo) -> SafeString:
        """Render the interactive focal-point editor used by admin JavaScript."""
        image_url = ""
        try:
            if obj and obj.image:
                image_url = obj.image.url
        except (ValueError, OSError):
            image_url = ""

        return format_html(
            """
            <div class="photo-crop-editor" data-photo-crop-editor data-image-url="{}">
                <div class="photo-crop-editor__intro">
                    <strong>Оберіть, яка частина фото буде в прев’ю</strong>
                    <p>
                        Перетягуйте фото всередині рамки або використовуйте стрілки.
                        Праворуч одразу видно, як цей самий фокус виглядатиме
                        у вертикальному форматі.
                    </p>
                </div>

                <div class="photo-crop-editor__previews">
                    <div class="photo-crop-editor__preview-group">
                        <span class="photo-crop-editor__label">Горизонтальне · 16:9</span>
                        <div
                            class="photo-crop-editor__stage photo-crop-editor__stage--landscape"
                            data-crop-stage
                            tabindex="0"
                            aria-label="Редагування горизонтального прев’ю"
                        >
                            <img alt="" data-crop-image draggable="false">
                            <span class="photo-crop-editor__grid" aria-hidden="true"></span>
                            <span class="photo-crop-editor__hint" data-crop-hint>
                                Перетягніть фото
                            </span>
                        </div>
                    </div>

                    <div class="photo-crop-editor__preview-group photo-crop-editor__preview-group--portrait">
                        <span class="photo-crop-editor__label">Вертикальне · 9:16</span>
                        <div
                            class="photo-crop-editor__stage photo-crop-editor__stage--portrait"
                            data-crop-stage
                            tabindex="0"
                            aria-label="Редагування вертикального прев’ю"
                        >
                            <img alt="" data-crop-image draggable="false">
                            <span class="photo-crop-editor__grid" aria-hidden="true"></span>
                        </div>
                    </div>
                </div>

                <div class="photo-crop-editor__footer">
                    <span>
                        Фокус: <output data-crop-position>50% × 50%</output>
                    </span>
                    <button type="button" class="button" data-crop-reset>
                        По центру
                    </button>
                </div>

                <p class="photo-crop-editor__empty" data-crop-empty>
                    Спочатку виберіть файл зображення.
                </p>
            </div>
            """,
            image_url,
        )

    @admin.display(description="Оригінал")
    def large_preview(self, obj: Photo) -> SafeString | str:
        """Render the uncropped source image on the edit page."""
        try:
            if not obj.pk or not obj.image:
                return "Збережіть фото, щоб побачити оригінал."
            return format_html(
                '<img src="{}" style="max-width:500px;max-height:350px;'
                'object-fit:contain;border-radius:6px;">',
                obj.image.url,
            )
        except (ValueError, OSError):
            return "Не вдалося відкрити файл зображення."
