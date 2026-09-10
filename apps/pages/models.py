from django.db import models


class HomePage(models.Model):
    """Контент головної сторінки.

    На сайті має існувати лише один запис.
    """

    # Перший екран

    hero_eyebrow = models.CharField(
        "Текст над ім’ям",
        max_length=100,
        default="Світла пам’ять",
    )

    hero_primary_button_label = models.CharField(
        "Текст кнопки переходу до історії",
        max_length=100,
        default="Прочитати історію",
    )

    hero_secondary_button_label = models.CharField(
        "Текст кнопки переходу до фото",
        max_length=100,
        default="Переглянути фото",
    )

    hero_scroll_label = models.CharField(
        "Підказка прокручування",
        max_length=150,
        default="Гортайте, щоб дізнатися більше",
    )

    hero_portrait_empty_label = models.CharField(
        "Текст, якщо головне фото не додано",
        max_length=150,
        default="Головне фото ще не додано",
    )

    empty_title = models.CharField(
        "Заголовок, якщо біографію ще не заповнено",
        max_length=200,
        default="Сторінка пам’яті",
    )

    empty_text = models.TextField(
        "Текст, якщо біографію ще не заповнено",
        default="Інформація ще готується до публікації.",
    )

    # Цитата

    quote_subtitle = models.CharField(
        "Текст під головною цитатою",
        max_length=200,
        default="Цитати, що склалися в характер.",
    )

    # Життя

    life_eyebrow = models.CharField(
        "Підпис блоку життя",
        max_length=100,
        default="Його життя",
    )

    life_title = models.CharField(
        "Заголовок блоку життя",
        max_length=200,
        default="Історія людини, яку пам’ятають",
    )

    life_description = models.TextField(
        "Опис блоку життя",
        default=(
            "Біографія, важливі дати та підтверджені родиною події — "
            "без вигаданих деталей і зайвої публічності."
        ),
    )

    life_empty_text = models.CharField(
        "Текст, якщо подій ще немає",
        max_length=200,
        default="Хронологію ще додають.",
    )

    life_more_label = models.CharField(
        "Текст посилання на історію",
        max_length=100,
        default="Читати далі",
    )

    # Фото

    gallery_eyebrow = models.CharField(
        "Підпис блоку фото",
        max_length=100,
        default="Фотоархів",
    )

    gallery_title = models.CharField(
        "Заголовок блоку фото",
        max_length=200,
        default="Моменти життя",
    )

    gallery_empty_text = models.CharField(
        "Текст, якщо фото ще немає",
        max_length=200,
        default="Фотоархів ще наповнюється",
    )

    gallery_button_label = models.CharField(
        "Текст кнопки фотоархіву",
        max_length=100,
        default="Відкрити весь фотоархів",
    )

    # Відео

    video_eyebrow = models.CharField(
        "Підпис блоку відео",
        max_length=100,
        default="Відео",
    )

    video_empty_title = models.CharField(
        "Заголовок, якщо рекомендованого відео немає",
        max_length=200,
        default="Голос і живі спогади",
    )

    video_empty_description = models.TextField(
        "Опис, якщо рекомендованого відео немає",
        default=(
            "Інтерв’ю, архівні записи та матеріали вшанування "
            "з короткими текстовими описами."
        ),
    )

    video_button_label = models.CharField(
        "Текст посилання на відео",
        max_length=100,
        default="Дивитися відео",
    )

    # Посилання

    links_eyebrow = models.CharField(
        "Підпис блоку посилання",
        max_length=100,
        default="Посилання",
    )

    links_empty_title = models.CharField(
        "Заголовок, якщо рекомендованого посилання немає",
        max_length=200,
        default="Матеріали та офіційні джерела",
    )

    links_empty_description = models.TextField(
        "Опис, якщо рекомендованого посилання немає",
        default=(
            "Добірка перевірених посилань на статті, "
            "новини та офіційні документи."
        ),
    )

    links_source_button_label = models.CharField(
        "Текст посилання на зовнішнє джерело",
        max_length=100,
        default="Відкрити джерело",
    )

    links_archive_button_label = models.CharField(
        "Текст переходу до всіх посилань",
        max_length=100,
        default="Перейти до матеріалів",
    )

    # Спогади

    memories_eyebrow = models.CharField(
        "Підпис блоку спогадів",
        max_length=100,
        default="Спогади",
    )

    memories_button_label = models.CharField(
        "Текст кнопки переходу до спогадів",
        max_length=100,
        default="Читати спогади",
    )

    updated_at = models.DateTimeField(
        "Оновлено",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Головна"
        verbose_name_plural = "Головна"

    def __str__(self) -> str:
        return "Головна"

class LifePage(models.Model):
    """Контент сторінки «Життя».

    На сайті має існувати лише один запис.
    """

    # Перший екран

    hero_eyebrow = models.CharField(
        "Текст над заголовком",
        max_length=100,
        default="Про нього",
    )

    hero_description = models.TextField(
        "Опис першого екрану",
        default=(
            "Людина поза подвигом: дитинство, навчання, родина, "
            "інтереси й підтверджена хронологія життя."
        ),
    )

    page_title_fallback = models.CharField(
        "Назва в заголовку браузера, якщо біографії немає",
        max_length=150,
        default="Сторінка пам’яті",
    )

    # Біографія

    portrait_empty_label = models.CharField(
        "Текст, якщо портрет не додано",
        max_length=150,
        default="Портрет ще не додано",
    )

    birth_date_label = models.CharField(
        "Підпис дати народження",
        max_length=100,
        default="Народився",
    )

    death_date_label = models.CharField(
        "Підпис дати смерті",
        max_length=100,
        default="Дата смерті",
    )

    rank_label = models.CharField(
        "Підпис звання",
        max_length=100,
        default="Звання",
    )

    award_label = models.CharField(
        "Підпис нагороди",
        max_length=100,
        default="Нагорода",
    )

    principle_label = models.CharField(
        "Підпис життєвого принципу",
        max_length=100,
        default="Життєвий принцип",
    )

    empty_biography_text = models.TextField(
        "Текст, якщо життєпис ще не додано",
        default="Повний життєпис ще готується до публікації.",
    )

    empty_page_text = models.TextField(
        "Текст, якщо біографію ще не заповнено",
        default="Інформація для цієї сторінки ще готується.",
    )

    # Хронологія

    timeline_eyebrow = models.CharField(
        "Підпис блоку хронології",
        max_length=100,
        default="Хронологія",
    )

    timeline_title = models.CharField(
        "Заголовок блоку хронології",
        max_length=200,
        default="Ключові події",
    )

    timeline_description = models.TextField(
        "Опис блоку хронології",
        default=(
            "До публікації додаються лише події з підтвердженими "
            "датами та формулюваннями."
        ),
    )

    timeline_empty_title = models.CharField(
        "Заголовок, якщо подій ще немає",
        max_length=200,
        default="Хронологія ще наповнюється",
    )

    timeline_empty_text = models.TextField(
        "Текст, якщо подій ще немає",
        default=(
            "Підтверджені події з’являться тут після додавання."
        ),
    )

    # Фото

    photos_eyebrow = models.CharField(
        "Підпис блоку фото",
        max_length=100,
        default="Фото до історії",
    )

    photos_title = models.CharField(
        "Заголовок блоку фото",
        max_length=200,
        default="Роки, що залишилися у світлинах",
    )

    childhood_photo = models.ForeignKey(
        "gallery.Photo",
        verbose_name="Фото для картки «Дитинство»",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        limit_choices_to={"is_published": True},
        help_text=(
            "Оберіть опубліковане фото, яке буде показано "
            "в картці «Дитинство»."
        ),
    )

    study_photo = models.ForeignKey(
        "gallery.Photo",
        verbose_name="Фото для картки «Навчання»",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        limit_choices_to={"is_published": True},
        help_text=(
            "Оберіть опубліковане фото, яке буде показано "
            "в картці «Навчання»."
        ),
    )

    family_photo = models.ForeignKey(
        "gallery.Photo",
        verbose_name="Фото для картки «Родина»",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        limit_choices_to={"is_published": True},
        help_text=(
            "Оберіть опубліковане фото, яке буде показано "
            "в картці «Родина»."
        ),
    )

    photos_childhood_label = models.CharField(
        "Підпис фото дитинства",
        max_length=100,
        default="Дитинство",
    )

    photos_study_label = models.CharField(
        "Підпис фото навчання",
        max_length=100,
        default="Навчання",
    )

    photos_family_label = models.CharField(
        "Підпис сімейного фото",
        max_length=100,
        default="Родина",
    )

    photos_more_label = models.CharField(
        "Текст переходу з фото",
        max_length=100,
        default="Дивитись більше",
    )

    photos_archive_label = models.CharField(
        "Текст переходу до фотоархіву",
        max_length=150,
        default="Перейти до фотоархіву",
    )

    updated_at = models.DateTimeField(
        "Оновлено",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Життя"
        verbose_name_plural = "Життя"

    def __str__(self) -> str:
        return "Життя"

class PhotoPage(models.Model):
    """Контент сторінки «Фото».

    На сайті має існувати лише один запис.
    """

    # Перший екран

    hero_eyebrow = models.CharField(
        "Текст над заголовком",
        max_length=200,
        default="Фотоархів",
    )

    hero_description = models.TextField(
        "Опис першого екрану",
        default="Основний архів світлин, згрупований за періодами життя.",
    )

    verification_note = models.TextField(
        "Примітка про перевірку фото",
        blank=True,
        default="Кожне фото публікується лише після перевірки.",
    )

    # Галерея

    show_more_label = models.CharField(
        "Текст кнопки завантаження наступних фото",
        max_length=100,
        default="Показати більше",
    )

    # Додаткові тексти

    category_empty_text = models.CharField(
        "Текст, якщо у вибраній категорії немає фото",
        max_length=250,
        default="У цій категорії поки немає фотографій.",
    )

    empty_title = models.CharField(
        "Заголовок, якщо фотоархів порожній",
        max_length=200,
        default="Фотоархів ще наповнюється",
    )

    empty_text = models.TextField(
        "Текст, якщо фотоархів порожній",
        default=(
            "Перевірені родиною фотографії "
            "з’являться тут після публікації."
        ),
    )

    updated_at = models.DateTimeField(
        "Оновлено",
        auto_now=True,
    )

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фото"

    def __str__(self) -> str:
        return "Фото"


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
