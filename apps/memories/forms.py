from django import forms

from apps.core.models import SiteSettings

from .models import MEMORY_TEXT_MAX_LENGTH, Memory, MemoryCategory


class MemoryForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}),
    )
    consent = forms.BooleanField(required=True)

    class Meta:
        model = Memory
        fields = ("author_name", "category", "text")
        widgets = {
            "author_name": forms.TextInput(attrs={"autocomplete": "name"}),
            "category": forms.Select(),
            "text": forms.Textarea(
                attrs={"rows": 6, "maxlength": MEMORY_TEXT_MAX_LENGTH}
            ),
        }

    def __init__(self, *args, site_settings=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.copy = site_settings if site_settings is not None else SiteSettings.load()
        for field, setting in (
            ("author_name", "name"),
            ("category", "category"),
            ("text", "text"),
            ("consent", "consent"),
        ):
            self.fields[field].label = getattr(self.copy, f"memories_{setting}_label")
        self.fields["author_name"].widget.attrs["placeholder"] = (
            self.copy.memories_name_placeholder
        )
        self.fields["text"].widget.attrs["placeholder"] = (
            self.copy.memories_text_placeholder
        )
        self.fields["category"].queryset = MemoryCategory.objects.filter(
            is_active=True
        ).order_by("sort_order", "id")
        self.fields["category"].empty_label = self.copy.memories_category_placeholder
        for field in self.fields.values():
            field.error_messages["required"] = self.copy.memories_required_error
        self.fields["category"].error_messages["invalid_choice"] = (
            self.copy.memories_invalid_error
        )
        self.fields["text"].error_messages["max_length"] = (
            self.copy.memories_limit_message
        )

    def clean_website(self):
        if self.cleaned_data.get("website", ""):
            raise forms.ValidationError(self.copy.memories_error_message)
        return ""

    def clean_author_name(self):
        name = self.cleaned_data["author_name"].strip()
        if len(name) < 2:
            raise forms.ValidationError(self.copy.memories_name_error)
        return name

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if len(text) < 10:
            raise forms.ValidationError(self.copy.memories_text_error)
        if len(text) > MEMORY_TEXT_MAX_LENGTH:
            raise forms.ValidationError(self.copy.memories_limit_message)
        return text
