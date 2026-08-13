from django.db import models


class ServicePage(models.Model):
    """Контент сторінки «Подвиг і служба».

    На сайті має існувати лише один запис.
    """

    class PublicationStatus(models.TextChoices):
        DRAFT = "draft", "Чернетка"
        NEEDS_APPROVAL = "needs_approval", "Потрібне погодження"
        APPROVED = "approved", "Погоджено до публікації"

    hero_eyebrow = models.CharField(
        "Позначка над заголовком",
        max_length=150,
        default="Офіційно узгоджений розділ",
    )
    hero_title = models.CharField(
        "Заголовок сторінки",
        max_length=150,
        default="Подвиг і служба",
    )
    hero_description = models.TextField(
        "Опис у першому екрані",
        blank=True,
    )
    publication_status = models.CharField(
        "Статус публікації",
        max_length=30,
        choices=PublicationStatus.choices,
        default=PublicationStatus.NEEDS_APPROVAL,
    )

    service_intro = models.TextField(
        "Основний опис служби",
        blank=True,
    )
    service_text = models.TextField(
        "Додатковий текст",
        blank=True,
    )
    editorial_note = models.TextField(
        "Редакційна примітка",
        blank=True,
    )

    award_title = models.CharField(
        "Назва нагороди",
        max_length=255,
        blank=True,
    )
    award_subtitle = models.CharField(
        "Уточнення про нагороду",
        max_length=255,
        blank=True,
        help_text="Наприклад: Орден «Золота Зірка» (посмертно)",
    )
    decree_date = models.DateField(
        "Дата указу",
        null=True,
        blank=True,
    )
    decree_number = models.CharField(
        "Номер указу",
        max_length=100,
        blank=True,
    )
    decree_source_name = models.CharField(
        "Назва офіційного джерела",
        max_length=255,
        blank=True,
        default="president.gov.ua",
    )
    decree_url = models.URLField(
        "Посилання на текст указу",
        blank=True,
    )

    is_published = models.BooleanField(
        "Показувати сторінку",
        default=False,
        help_text="Увімкніть після погодження матеріалів.",
    )
    updated_at = models.DateTimeField(
        "Оновлено",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Подвиг і служба"
        verbose_name_plural = "Подвиг і служба"

    def __str__(self) -> str:
        return self.hero_title