from django.db import models


MEMORY_TEXT_MAX_LENGTH = 15_000

class MemoryCategory(models.Model):
    name = models.CharField(
        "Назва",
        max_length=255,
    )
    sort_order = models.PositiveSmallIntegerField(
        "Порядок",
        default=0,
    )
    is_active = models.BooleanField(
        "Активна",
        default=True,
    )

    class Meta:
        verbose_name = "Категорія спогадів"
        verbose_name_plural = "Категорії спогадів"
        ordering = ("sort_order", "id")

    def __str__(self):
        return self.name

class Memory(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "На модерації"
        APPROVED = "approved", "Опубліковано"
        REJECTED = "rejected", "Відхилено"

    author_name = models.CharField("Імʼя", max_length=255)
    author_role = models.CharField(
        "Хто автор",
        max_length=255,
        blank=True,
        help_text="Наприклад: «побратим, позивний «Сокіл»»",
    )
    category = models.ForeignKey(
        MemoryCategory,
        verbose_name="Категорія",
        on_delete=models.PROTECT,
        related_name="memories",
        null=True,
        blank=True,
    )
    text = models.TextField(
        "Текст спогаду",
        max_length=MEMORY_TEXT_MAX_LENGTH,
    )
    featured = models.BooleanField(
        "Показувати на головній",
        default=False,
        help_text="Лише один спогад варто позначати як featured",
    )
    status = models.CharField(
        "Статус", max_length=20, choices=Status.choices, default=Status.PENDING
    )
    created_at = models.DateTimeField("Створено", auto_now_add=True)

    class Meta:
        verbose_name = "Спогад"
        verbose_name_plural = "Спогади"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author_name}: {self.text[:40]}"
