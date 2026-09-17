from django.db import models
from modeltranslation.translator import TranslationOptions, register

from .models import SiteSettings


@register(SiteSettings)
class SiteSettingsTranslationOptions(TranslationOptions):
    fields = tuple(
        field.name
        for field in SiteSettings._meta.fields
        if isinstance(field, (models.CharField, models.TextField))
        and field.name
        not in {
            "brand_letter",
        }
    )


# Explicit English defaults also apply to newly created settings.
ENGLISH_COPY_DEFAULTS = {
    "memories_name_label": "Name or signature",
    "memories_name_placeholder": "For example: Ivan or the callsign “Falcon”",
    "memories_category_label": "How did you know them?",
    "memories_category_placeholder": "Choose an option",
    "memories_text_label": "Your memory",
    "memories_text_placeholder": "Write your memory",
    "memories_text_hint": "Long memories are shortened in the feed. Use “Read more” to open the full text.",
    "memories_consent_label": "I agree to publication after moderator review.",
    "memories_more_label": "Read more",
    "memories_limit_message": "The 15,000-character limit has been reached. Submit this memory and send the continuation in another form.",
    "memories_name_error": "Enter a name or signature of at least two characters.",
    "memories_text_error": "A memory must contain at least 10 characters.",
    "memories_required_error": "This field is required.",
    "memories_invalid_error": "Please check this field.",
    "memories_close_label": "Close",
    "memories_close_dialog_label": "Close memory",
    "memories_characters_label": "characters",
    "memories_escape_label": "Esc — close",
    "footer_dedication": "This page was created in loving memory of Nazar Borovytskyi",
    "language_label": "Language",
    "mobile_language_label": "LANGUAGE / МОВА",
    "photos_all_label": "All photos",
    "videos_date_label": "Recording date",
    "videos_category_label": "Category",
    "videos_duration_label": "Duration",
    "demo_title": "Demonstration layout.",
    "demo_text": "All personal details and materials are placeholders and must be replaced after review by the family.",
    "photo_category_family": "Family and childhood",
    "photo_category_study": "Education",
    "photo_category_service": "Service and comrades",
    "photo_category_memory": "Remembrance",
    "video_category_family": "Family archive",
    "video_category_interview": "Interview",
    "video_category_service": "Service",
    "video_category_memory": "Remembrance",
    "video_category_media": "Media coverage",
    "video_category_other": "Other",
}

for name, default in ENGLISH_COPY_DEFAULTS.items():
    SiteSettings._meta.get_field(f"{name}_en").default = default
