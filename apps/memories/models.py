from django.db import models


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
    text = models.TextField(
        "Текст спогаду",
        max_length=1500,
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
