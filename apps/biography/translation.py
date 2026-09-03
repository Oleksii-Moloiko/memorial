from modeltranslation.translator import TranslationOptions, register

from .models import Biography, TimelineEvent


@register(Biography)
class BiographyTranslationOptions(TranslationOptions):
    fields = (
        "full_name",
        "rank",
        "award_title",
        "intro_text",
        "signature_quote",
        "summary",
        "full_text",
    )


@register(TimelineEvent)
class TimelineEventTranslationOptions(TranslationOptions):
    fields = (
        "date_label",
        "title",
        "description",
    )