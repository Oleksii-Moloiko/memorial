from django.contrib import admin, messages
from django.db import DatabaseError, transaction
from django.db.models import QuerySet
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import path

from .models import Memory


@admin.register(Memory)
class MemoryAdmin(admin.ModelAdmin):
    """Admin configuration for reviewing and publishing memories."""
    change_list_template = "admin/memories/memory/change_list.html"

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

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "<int:memory_id>/approve/",
                self.admin_site.admin_view(self.approve_memory_view),
                name="memories_memory_approve",
            ),
            path(
                "<int:memory_id>/reject/",
                self.admin_site.admin_view(self.reject_memory_view),
                name="memories_memory_reject",
            ),
        ]

        return custom_urls + urls

    def approve_memory_view(
            self,
            request: HttpRequest,
            memory_id: int,
    ):
        if request.method != "POST":
            return redirect("admin:memories_memory_changelist")

        memory = get_object_or_404(Memory, pk=memory_id)

        memory.status = Memory.Status.APPROVED
        memory.save(update_fields=["status"])

        self.message_user(
            request,
            f"Спогад від {memory.author_name} опубліковано.",
            level=messages.SUCCESS,
        )

        return redirect("admin:memories_memory_changelist")

    def reject_memory_view(
            self,
            request: HttpRequest,
            memory_id: int,
    ):
        if request.method != "POST":
            return redirect("admin:memories_memory_changelist")

        memory = get_object_or_404(Memory, pk=memory_id)

        memory.status = Memory.Status.REJECTED
        memory.featured = False
        memory.save(
            update_fields=[
                "status",
                "featured",
            ]
        )

        self.message_user(
            request,
            f"Спогад від {memory.author_name} відхилено.",
            level=messages.SUCCESS,
        )

        return redirect("admin:memories_memory_changelist")

    def changelist_view(
            self,
            request: HttpRequest,
            extra_context=None,
    ):
        extra_context = extra_context or {}

        extra_context["pending_count"] = Memory.objects.filter(
            status=Memory.Status.PENDING,
        ).count()

        extra_context["approved_count"] = Memory.objects.filter(
            status=Memory.Status.APPROVED,
        ).count()

        extra_context["rejected_count"] = Memory.objects.filter(
            status=Memory.Status.REJECTED,
        ).count()

        return super().changelist_view(
            request,
            extra_context=extra_context,
        )

    def save_model(
            self,
            request: HttpRequest,
            obj: Memory,
            form,
            change: bool,
    ) -> None:
        if obj.featured:
            if obj.status != Memory.Status.APPROVED:
                obj.featured = False

                self.message_user(
                    request,
                    (
                        "Спогад не позначено для головної: "
                        "спочатку його потрібно опублікувати."
                    ),
                    level=messages.WARNING,
                )

            else:
                Memory.objects.exclude(
                    pk=obj.pk,
                ).update(featured=False)

        super().save_model(
            request,
            obj,
            form,
            change,
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
