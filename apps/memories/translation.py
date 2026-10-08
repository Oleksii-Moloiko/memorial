from modeltranslation.translator import TranslationOptions, register

from .models import Memory, MemoryCategory


@register(Memory)
class MemoryTranslationOptions(TranslationOptions):
    fields = ("text",)


@register(MemoryCategory)
class MemoryCategoryTranslationOptions(TranslationOptions):
    fields = ("name",)