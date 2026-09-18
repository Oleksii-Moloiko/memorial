import json

from django import forms
from django.contrib import admin
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.urls import path, reverse
from django.utils.html import format_html
from django.utils.safestring import SafeString
from modeltranslation.admin import TranslationAdmin

from django.utils import timezone

from .models import Video, VideoUpload
from .services import create_video_upload, confirm_video_upload


class VideoAdminForm(forms.ModelForm):
    video_file = forms.FileField(
        label="Відеофайл",
        required=False,
        widget=forms.FileInput(
            attrs={
                "accept": ".mp4,.webm,.mov,video/mp4,video/webm,video/quicktime",
            }
        ),
        help_text=(
            "Дозволені формати: MP4, WebM або MOV. "
            "Максимальний розмір — 300 MB."
        ),
    )

    video_upload_id = forms.UUIDField(
        required=False,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Video
        fields = "__all__"

    def __init__(self, *args, request_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.request_user = request_user
        self.video_upload = None

    def clean(self):
        cleaned_data = super().clean()

        video_file = cleaned_data.get("video_file")
        upload_id = cleaned_data.get("video_upload_id")

        new_video_file = self.files.get("video_file")

        if upload_id and new_video_file:
            self.add_error(
                "video_file",
                "Відео вже завантажено окремо. "
                "Повторне завантаження файлу не потрібне.",
            )

        if upload_id:
            if not self.request_user:
                self.add_error(
                    "video_file",
                    "Не вдалося визначити користувача.",
                )
            else:
                try:
                    upload = VideoUpload.objects.get(
                        id=upload_id,
                        created_by=self.request_user,
                    )
                except VideoUpload.DoesNotExist:
                    self.add_error(
                        "video_file",
                        "Завантаження відео не знайдено.",
                    )
                else:
                    if upload.status != VideoUpload.Status.VERIFIED:
                        self.add_error(
                            "video_file",
                            "Відео ще не завершило завантаження.",
                        )
                    else:
                        self.video_upload = upload

        # Новий Video обов'язково повинен мати або звичайний файл,
        # або вже підтверджений direct upload.
        if (
            not self.instance.pk
            and not video_file
            and self.video_upload is None
        ):
            self.add_error(
                "video_file",
                "Оберіть відеофайл і дочекайтеся завершення завантаження.",
            )

        if (
            cleaned_data.get("is_featured")
            and not cleaned_data.get("is_published")
        ):
            self.add_error(
                "is_featured",
                (
                    "Рекомендованим може бути лише відео, "
                    "яке показується на сайті."
                ),
            )

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        if self.video_upload is not None:
            instance.video_file.name = self.video_upload.object_key

        if commit:
            instance.save()
            self.save_m2m()

        return instance

@admin.register(Video)
class VideoAdmin(TranslationAdmin):
    """Admin configuration for memorial videos."""
    form = VideoAdminForm

    class Media:
        css = {
            "all": (
                "admin/css/video_upload.css",
            ),
        }

        js = (
            "admin/js/video_upload.js",
        )

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "upload/start/",
                self.admin_site.admin_view(self.start_video_upload),
                name="videos_video_upload_start",
            ),
            path(
                "upload/confirm/",
                self.admin_site.admin_view(self.confirm_video_upload),
                name="videos_video_upload_confirm",
            ),
        ]

        return custom_urls + urls

    def _check_upload_permission(self, request):
        if not (
            self.has_add_permission(request)
            or self.has_change_permission(request)
        ):
            raise PermissionDenied

    def start_video_upload(self, request):
        self._check_upload_permission(request)

        if request.method != "POST":
            return JsonResponse(
                {"error": "Метод не підтримується."},
                status=405,
            )

        try:
            payload = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"error": "Некоректний JSON."},
                status=400,
            )

        original_name = payload.get("name")
        declared_size = payload.get("size")
        content_type = payload.get("content_type", "")

        if not original_name:
            return JsonResponse(
                {"error": "Не вказано ім’я файлу."},
                status=400,
            )

        try:
            declared_size = int(declared_size)
        except (TypeError, ValueError):
            return JsonResponse(
                {"error": "Некоректний розмір файлу."},
                status=400,
            )

        try:
            upload, upload_url = create_video_upload(
                user=request.user,
                original_name=original_name,
                declared_size=declared_size,
                content_type=content_type,
            )
        except ValidationError as exc:
            return JsonResponse(
                {"error": exc.messages[0]},
                status=400,
            )

        return JsonResponse(
            {
                "upload_id": str(upload.id),
                "upload_url": upload_url,
            }
        )

    def confirm_video_upload(self, request):
        self._check_upload_permission(request)

        if request.method != "POST":
            return JsonResponse(
                {"error": "Метод не підтримується."},
                status=405,
            )

        try:
            payload = json.loads(request.body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse(
                {"error": "Некоректний JSON."},
                status=400,
            )

        upload_id = payload.get("upload_id")

        if not upload_id:
            return JsonResponse(
                {"error": "Не вказано upload_id."},
                status=400,
            )

        try:
            upload = confirm_video_upload(
                user=request.user,
                upload_id=upload_id,
            )
        except (ValidationError, ValueError) as exc:
            if isinstance(exc, ValidationError):
                message = exc.messages[0]
            else:
                message = "Некоректний upload_id."

            return JsonResponse(
                {"error": message},
                status=400,
            )

        return JsonResponse(
            {
                "upload_id": str(upload.id),
                "status": upload.status,
                "size": upload.actual_size,
            }
        )

    def get_form(self, request, obj=None, **kwargs):
        base_form = super().get_form(request, obj, **kwargs)

        video_field = base_form.base_fields.get("video_file")

        if video_field:
            video_field.widget.attrs.update(
                {
                    "data-upload-start-url": reverse(
                        "admin:videos_video_upload_start"
                    ),
                    "data-upload-confirm-url": reverse(
                        "admin:videos_video_upload_confirm"
                    ),
                    "data-has-existing-video": (
                        "1"
                        if obj and obj.video_file
                        else "0"
                    ),
                }
            )

        class RequestAwareVideoAdminForm(base_form):
            def __init__(self, *args, **form_kwargs):
                form_kwargs["request_user"] = request.user
                super().__init__(*args, **form_kwargs)

        return RequestAwareVideoAdminForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        upload = getattr(form, "video_upload", None)

        if upload is not None:
            VideoUpload.objects.filter(
                pk=upload.pk,
                status=VideoUpload.Status.VERIFIED,
            ).update(
                status=VideoUpload.Status.ATTACHED,
                attached_at=timezone.now(),
            )

    list_display = (
        "thumbnail_preview",
        "title",
        "category",
        "recorded_at",
        "is_featured",
        "is_published",
        "order",
    )
    list_display_links = ("thumbnail_preview", "title")
    list_editable = ("is_featured", "is_published", "order")
    list_filter = ("category", "is_featured", "is_published", "created_at")
    search_fields = ("title", "description", "recorded_at", "transcript")
    readonly_fields = (
        "large_thumbnail_preview",
        "video_preview",
    )
    date_hierarchy = "created_at"
    ordering = ("order", "id")
    list_per_page = 30
    save_on_top = True
    fieldsets = (
        (
            "ВІДЕО",
            {
                "fields": (
                    "video_file",
                    "video_upload_id",
                    "video_preview",
                    "thumbnail",
                    "large_thumbnail_preview",
                )
            },
        ),
        (
            "ОСНОВНА ІНФОРМАЦІЯ",
            {
                "fields": (
                    "title",
                    "description",
                )
            },
        ),
        (
            "КЛАСИФІКАЦІЯ",
            {
                "fields": (
                    "category",
                    "recorded_at",
                    "duration",
                )
            },
        ),
        (
            "ДОСТУПНІСТЬ",
            {"fields": ("transcript",)},
        ),
        (
            "ПУБЛІКАЦІЯ",
            {
                "fields": (
                    "is_featured",
                    "is_published",
                    "order",
                )
            },
        ),
    )

    @admin.display(description="Обкладинка")
    def thumbnail_preview(self, obj: Video) -> SafeString | str:
        """Render a compact thumbnail preview."""
        try:
            if not obj.thumbnail:
                return "—"
            return format_html(
                '<img src="{}" style="display:block;width:90px;max-width:100%;'
                'height:50px;object-fit:cover;border-radius:4px;">',
                obj.thumbnail.url,
            )
        except (ValueError, OSError):
            return "Файл недоступний"

    @admin.display(description="Перегляд обкладинки")
    def large_thumbnail_preview(self, obj: Video) -> SafeString | str:
        """Render a large thumbnail preview."""
        try:
            if not obj.pk or not obj.thumbnail:
                return "Обкладинку ще не додано."
            return format_html(
                '<img src="{}" style="display:block;width:100%;max-width:500px;'
                'height:auto;max-height:280px;object-fit:contain;">',
                obj.thumbnail.url,
            )
        except (ValueError, OSError):
            return "Не вдалося відкрити обкладинку."

    @admin.display(description="Перегляд відео")
    def video_preview(self, obj: Video) -> SafeString | str:
        """Render an HTML5 video player on the edit page."""
        try:
            if not obj.pk or not obj.video_file:
                return "Збережіть відео, щоб побачити перегляд."
            return format_html(
                '<video controls preload="metadata" '
                'style="display:block;width:100%;max-width:600px;height:auto;">'
                '<source src="{}">'
                "Ваш браузер не підтримує відео."
                "</video>",
                obj.video_file.url,
            )
        except (ValueError, OSError):
            return "Не вдалося відкрити відеофайл."
