from modeltranslation.translator import TranslationOptions, register

from .models import Video


@register(Video)
class VideoTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "description",
        "recorded_at",
        "transcript",
    )