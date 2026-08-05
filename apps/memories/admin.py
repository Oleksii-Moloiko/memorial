from django.contrib import admin, messages
from django.db import DatabaseError, transaction
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Memory


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    """Admin configuration for reviewing and publishing memories."""

    list_display = (
        "author_name",
        "author_role",
        "short_text",
        "status",
        "featured",
        "created_at",
    )
    list_editable = ("status", "featured")
    list_filter = ("status", "featured", "created_at")
    search_fields = ("author_name", "author_role", "text")
    readonly_fields = ("created_at",)
    date_hierarchy = "created_at"
    ordering = ("-created_at",)
    list_per_page = 30
    save_on_top = True
    actions = (
        "approve_memories",
        "reject_memories",
        "move_to_moderation",
        "set_featured_memory",
    )
    fieldsets = (
        (
            "Автор",
            {"fields": ("author_name", "author_role")},
        ),
        (
            "Спогад",
            {"fields": ("text",)},
        ),
        (
            "Модерація",
            {"fields": ("status", "featured", "created_at")},
        ),
    )

    @admin.display(description="Текст")
    def short_text(self, obj: Memory) -> str:
        """Return a compact memory excerpt for the list page."""
        return f"{obj.text[:90]}…" if len(obj.text) > 90 else obj.text

    @admin.action(description="Опублікувати вибрані спогади")
    def approve_memories(
        self,
        request: HttpRequest,
        queryset: QuerySet[Memory],
    ) -> None:
        """Mark selected memories as approved."""
        self._update_status(request, queryset, Memory.Status.APPROVED)

    @admin.action(description="Відхилити вибрані спогади")
    def reject_memories(
        self,
        request: HttpRequest,
        queryset: QuerySet[Memory],
    ) -> None:
        """Mark selected memories as rejected."""
        self._update_status(request, queryset, Memory.Status.REJECTED)

    @admin.action(description="Повернути вибрані на модерацію")
    def move_to_moderation(
        self,
        request: HttpRequest,
        queryset: QuerySet[Memory],
    ) -> None:
        """Move selected memories back to pending moderation."""
        self._update_status(request, queryset, Memory.Status.PENDING)

    @admin.action(description="Показувати вибраний спогад на головній")
    def set_featured_memory(
        self,
        request: HttpRequest,
        queryset: QuerySet[Memory],
    ) -> None:
        """Set exactly one approved memory as featured."""
        if queryset.count() != 1:
            self.message_user(
                request,
                "Оберіть рівно один спогад.",
                level=messages.WARNING,
            )
            return

        memory = queryset.first()
        if memory is None:
            return

        if memory.status != Memory.Status.APPROVED:
            self.message_user(
                request,
                "На головній можна показувати лише опублікований спогад.",
                level=messages.WARNING,
            )
            return

        try:
            with transaction.atomic():
                Memory.objects.exclude(pk=memory.pk).update(featured=False)
                Memory.objects.filter(pk=memory.pk).update(featured=True)
        except DatabaseError:
            self.message_user(
                request,
                "Не вдалося оновити рекомендований спогад.",
                level=messages.ERROR,
            )
            return

        self.message_user(request, "Спогад додано на головну сторінку.")

    def _update_status(
        self,
        request: HttpRequest,
        queryset: QuerySet[Memory],
        status: str,
    ) -> None:
        """Update moderation status and report database errors."""
        try:
            updated = queryset.update(status=status)
        except DatabaseError:
            self.message_user(
                request,
                "Не вдалося оновити статус спогадів.",
                level=messages.ERROR,
            )
            return

        self.message_user(request, f"Оновлено спогадів: {updated}.")
