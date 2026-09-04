from modeltranslation.translator import TranslationOptions, register

from .models import ServiceAward, ServicePage, ServiceQuote


@register(ServicePage)
class ServicePageTranslationOptions(TranslationOptions):
    fields = (
        "hero_eyebrow",
        "hero_title",
        "hero_description",
        "service_intro",
        "service_text",
        "editorial_note",
        "award_title",
        "award_subtitle",
        "decree_source_name",
    )


@register(ServiceAward)
class ServiceAwardTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "subtitle",
        "decree_source_name",
    )


@register(ServiceQuote)
class ServiceQuoteTranslationOptions(TranslationOptions):
    fields = (
        "text",
        "context",
    )
