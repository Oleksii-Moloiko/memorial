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
    # Навігація по сторінці

    index_eyebrow = models.CharField(
        "Підпис навігації",
        max_length=100,
        default="На сторінці",
    )


    # Блок «Нагороди»

    awards_eyebrow = models.CharField(
        "Підпис блоку нагород",
        max_length=100,
        default="Нагороди",
    )

    awards_title = models.CharField(
        "Заголовок блоку нагород",
        max_length=255,
        default="Нагороди та відзнаки",
    )

    award_date_label = models.CharField(
        "Підпис дати указу",
        max_length=100,
        default="Дата указу",
    )

    award_number_label = models.CharField(
        "Підпис номера указу",
        max_length=100,
        default="Номер",
    )

    award_source_label = models.CharField(
        "Підпис джерела",
        max_length=100,
        default="Джерело",
    )


    # Блок «Цитати»

    quotes_eyebrow = models.CharField(
        "Підпис блоку цитат",
        max_length=100,
        default="Цитати",
    )

    quotes_title = models.CharField(
        "Заголовок блоку цитат",
        max_length=255,
        default="Слова, що залишилися",
    )

    quote_more_label = models.CharField(
        "Текст кнопки розгортання цитати",
        max_length=100,
        default="Дивитись більше",
    )


    # Блок «Посилання»

    links_eyebrow = models.CharField(
        "Підпис блоку посилань",
        max_length=100,
        default="Посилання",
    )

    links_title = models.CharField(
        "Заголовок блоку посилань",
        max_length=255,
        default="Матеріали та джерела",
    )

    links_missing_date_label = models.CharField(
        "Текст, якщо дата не вказана",
        max_length=100,
        default="Дата не вказана",
    )
    links_nav_label = models.CharField(
        "Назва в навігації",
        max_length=100,
        default="Посилання",
    )

    links_description = models.TextField(
        "Опис блоку посилань",
        blank=True,
        default=(
            "Перевірені посилання на публікації, офіційні документи "
            "й матеріали вшанування — без копіювання повних текстів."
        ),
    )

    links_verification_note = models.TextField(
        "Примітка про перевірку посилань",
        blank=True,
        default="Перевірка посилань рекомендована 1–2 рази на рік.",
    )

    links_empty_title = models.CharField(
        "Заголовок, якщо посилань немає",
        max_length=255,
        default="Матеріалів поки немає",
    )

    links_empty_text = models.TextField(
        "Текст, якщо посилань немає",
        blank=True,
        default=(
            "Перевірені публікації та офіційні джерела "
            "з’являться тут пізніше."
        ),
    )
    publication_status = models.CharField(
        "Статус публікації",
        max_length=30,
        choices=PublicationStatus.choices,
        default=PublicationStatus.NEEDS_APPROVAL,
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


class ServiceAward(models.Model):
    service_page = models.ForeignKey(
        ServicePage,
        on_delete=models.CASCADE,
        related_name="awards",
        verbose_name="Сторінка",
    )

    title = models.CharField(
        "Назва нагороди",
        max_length=255,
    )

    subtitle = models.CharField(
        "Уточнення",
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
    )

    decree_url = models.URLField(
        "Посилання на текст указу",
        blank=True,
    )

    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Нагорода"
        verbose_name_plural = "Нагороди"

    def __str__(self):
        return self.title


class ServiceQuote(models.Model):
    service_page = models.ForeignKey(
        ServicePage,
        on_delete=models.CASCADE,
        related_name="quotes",
        verbose_name="Сторінка",
    )

    text = models.TextField(
        "Цитата",
    )

    context = models.CharField(
        "Контекст / підпис",
        max_length=255,
        blank=True,
        help_text="Наприклад: із розмови з побратимами",
    )

    order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )

    class Meta:
        ordering = ("order", "id")
        verbose_name = "Цитата"
        verbose_name_plural = "Цитати"

    def __str__(self):
        return self.text[:80]
