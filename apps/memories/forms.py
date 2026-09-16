from django import forms
from django.utils.translation import gettext_lazy as _

from .models import (
    MEMORY_TEXT_MAX_LENGTH,
    Memory,
    MemoryCategory,
)

MEMORY_TEXT_LIMIT_MESSAGE = _(
    "Досягнуто ліміт в 15 000 символів. "
    "Надішліть цей спогад, а продовження — ще однією формою."
)


class MemoryForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                "tabindex": "-1",
                "autocomplete": "off",
            }
        ),
    )

    consent = forms.BooleanField(
        required=True,
        label=_("Погоджуюся на публікацію після перевірки модератором."),
    )

    class Meta:
        model = Memory
        fields = (
            "author_name",
            "category",
            "text",
        )

        labels = {
            "author_name": _("Ім’я або підпис"),
            "category": _("Ким ви були знайомі"),
            "text": _("Текст спогаду"),
        }

        widgets = {
            "author_name": forms.TextInput(
                attrs={
                    "placeholder": _("Наприклад: Іван або позивний «Сокіл»"),
                    "autocomplete": "name",
                }
            ),
            "category": forms.Select(),
            "text": forms.Textarea(
                attrs={
                    "rows": 6,
                    "maxlength": MEMORY_TEXT_MAX_LENGTH,
                    "placeholder": _("Напишіть спогад"),
                }
            ),
        }

        error_messages = {
            "text": {
                "max_length": MEMORY_TEXT_LIMIT_MESSAGE,
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["category"].queryset = MemoryCategory.objects.filter(
            is_active=True
        ).order_by("sort_order", "id")

        self.fields["category"].empty_label = _("Оберіть варіант")

    def clean_website(self):
        value = self.cleaned_data.get("website", "")

        if value:
            raise forms.ValidationError(_("Не вдалося надіслати форму."))

        return ""

    def clean_author_name(self):
        name = self.cleaned_data["author_name"].strip()
        if len(name) < 2:
            raise forms.ValidationError(
                _("Вкажіть ім’я або підпис щонайменше з двох символів.")
            )
        return name

    def clean_text(self):
        text = self.cleaned_data["text"].strip()

        if len(text) < 10:
            raise forms.ValidationError(_("Спогад має містити щонайменше 10 символів."))

        if len(text) > MEMORY_TEXT_MAX_LENGTH:
            raise forms.ValidationError(MEMORY_TEXT_LIMIT_MESSAGE)

        return text
