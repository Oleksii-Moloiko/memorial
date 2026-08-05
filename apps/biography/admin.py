from django.contrib import admin

from .models import Biography, TimelineEvent


@admin.register(Biography)
class BiographyAdmin(admin.ModelAdmin):
    list_display = ("full_name", "birth_date", "death_date")


@admin.register(TimelineEvent)
class TimelineEventAdmin(admin.ModelAdmin):
    list_display = ("date_label", "title", "order")
    list_editable = ("order",)
