from modeltranslation.translator import TranslationOptions, register

from .models import SeoPage


@register(SeoPage)
class SeoPageTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "description",
    )