from django.contrib import admin

from .models import MediaMention


@admin.register(MediaMention)
class MediaMentionAdmin(admin.ModelAdmin):
    list_display = ("source_name", "published_date", "order")
    list_editable = ("order",)
