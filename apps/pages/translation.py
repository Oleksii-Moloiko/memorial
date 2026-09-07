from modeltranslation.translator import TranslationOptions, register

from .models import ServiceAward, ServicePage, ServiceQuote


@register(ServicePage)
class ServicePageTranslationOptions(TranslationOptions):
    fields = (
        "hero_eyebrow",
        "hero_title",
        "hero_description",

        "index_eyebrow",

        "awards_eyebrow",
        "awards_title",
        "award_date_label",
        "award_number_label",
        "award_source_label",

        "quotes_eyebrow",
        "quotes_title",
        "quote_more_label",

        "links_eyebrow",
        "links_title",
        "links_missing_date_label",
        "links_nav_label",
        "links_description",
        "links_verification_note",
        "links_empty_title",
        "links_empty_text",
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