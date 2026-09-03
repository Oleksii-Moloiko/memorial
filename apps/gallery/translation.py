from modeltranslation.translator import TranslationOptions, register

from .models import Photo


@register(Photo)
class PhotoTranslationOptions(TranslationOptions):
    fields = (
        "caption",
        "alt_text",
    )