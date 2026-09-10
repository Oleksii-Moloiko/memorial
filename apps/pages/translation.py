from modeltranslation.translator import TranslationOptions, register

from .models import (
    HomePage,
    LifePage,
    PhotoPage,
    ServiceAward,
    ServicePage,
    ServiceQuote,
)


@register(HomePage)
class HomePageTranslationOptions(TranslationOptions):
    fields = (
        "hero_eyebrow",
        "hero_primary_button_label",
        "hero_secondary_button_label",
        "hero_scroll_label",
        "hero_portrait_empty_label",
        "empty_title",
        "empty_text",
        "quote_subtitle",
        "life_eyebrow",
        "life_title",
        "life_description",
        "life_empty_text",
        "life_more_label",
        "gallery_eyebrow",
        "gallery_title",
        "gallery_empty_text",
        "gallery_button_label",
        "video_eyebrow",
        "video_empty_title",
        "video_empty_description",
        "video_button_label",
        "links_eyebrow",
        "links_empty_title",
        "links_empty_description",
        "links_source_button_label",
        "links_archive_button_label",
        "memories_eyebrow",
        "memories_button_label",
    )

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

@register(LifePage)
class LifePageTranslationOptions(TranslationOptions):
    fields = (
        "hero_eyebrow",
        "hero_description",
        "page_title_fallback",
        "portrait_empty_label",
        "birth_date_label",
        "death_date_label",
        "rank_label",
        "award_label",
        "principle_label",
        "empty_biography_text",
        "empty_page_text",
        "timeline_eyebrow",
        "timeline_title",
        "timeline_description",
        "timeline_empty_title",
        "timeline_empty_text",
        "photos_eyebrow",
        "photos_title",
        "photos_childhood_label",
        "photos_study_label",
        "photos_family_label",
        "photos_more_label",
        "photos_archive_label",
    )

@register(PhotoPage)
class PhotoPageTranslationOptions(TranslationOptions):
    fields = (
        "hero_eyebrow",
        "hero_description",
        "verification_note",
        "show_more_label",
        "category_empty_text",
        "empty_title",
        "empty_text",
    )