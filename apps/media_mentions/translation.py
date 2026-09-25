from modeltranslation.translator import TranslationOptions, register

from .models import MediaMention


@register(MediaMention)
class MediaMentionTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "source_name",
    )
