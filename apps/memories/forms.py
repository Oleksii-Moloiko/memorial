from django import forms

from .models import Memory


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
        label="Погоджуюся на публікацію після перевірки модератором.",
    )

    class Meta:
        model = Memory
        fields = (
            "author_name",
            "author_role",
            "text",
        )

        labels = {
            "author_name": "Ім’я або підпис",
            "author_role": "Ким ви були знайомі",
            "text": "Текст спогаду",
        }

        widgets = {
            "author_name": forms.TextInput(
                attrs={
                    "placeholder": "Наприклад: Іван або позивний «Сокіл»",
                    "autocomplete": "name",
                }
            ),
            "author_role": forms.Select(
                choices=[
                    ("", "Оберіть варіант"),
                    ("Родина", "Родина"),
                    ("Друг / подруга", "Друг / подруга"),
                    ("Побратим", "Побратим"),
                    ("Однокласник / однокурсник", "Однокласник / однокурсник"),
                    ("Колега", "Колега"),
                    ("Інше", "Інше"),
                ]
            ),
            "text": forms.Textarea(
                attrs={
                    "rows": 6,
                    "maxlength": 1500,
                    "placeholder": "Напишіть спогад",
                }
            ),
        }

    def clean_author_name(self):
        author_name = self.cleaned_data["author_name"].strip()

        if len(author_name) < 2:
            raise forms.ValidationError(
                "Вкажіть ім’я або підпис щонайменше з двох символів."
            )

        return author_name

    def clean_website(self):
        value = self.cleaned_data.get("website", "")

        if value:
            raise forms.ValidationError(
                "Не вдалося надіслати форму."
            )

        return ""

    def clean_author_role(self):
        return self.cleaned_data.get("author_role", "").strip()

    def clean_text(self):
        text = self.cleaned_data["text"].strip()

        if len(text) < 10:
            raise forms.ValidationError("Спогад має містити щонайменше 10 символів.")

        if len(text) > 1500:
            raise forms.ValidationError("Спогад не може перевищувати 500 символів.")

        return text
