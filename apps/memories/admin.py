from django.contrib import admin

from .models import Memory


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    list_display = ("author_name", "author_role", "status", "featured", "created_at")
    list_editable = ("status", "featured")
    list_filter = ("status", "featured")
    search_fields = ("author_name", "text")
