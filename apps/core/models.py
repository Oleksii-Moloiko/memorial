from django.core.cache import cache
from django.db import models


class SiteSettings(models.Model):
    """Singleton з глобальними налаштуваннями сайту."""

    site_title = models.CharField(
        "Назва сайту",
        max_length=200,
        default="Memorial",
    )

    brand_letter = models.CharField(
        "Літера логотипа",
        max_length=4,
        blank=True,
    )

    site_name = models.CharField(
        "Назва в шапці",
        max_length=100,
        blank=True,
    )

    subtitle = models.CharField(
        "Підзаголовок у шапці",
        max_length=200,
        blank=True,
    )

    # Назви розділів

    home_title = models.CharField(
        "Назва розділу «Головна»",
        max_length=100,
        default="Головна",
    )

    life_title = models.CharField(
        "Назва розділу «Життя»",
        max_length=100,
        default="Життя",
    )

    service_title = models.CharField(
        "Назва розділу «Подвиг і служба»",
        max_length=100,
        default="Подвиг і служба",
    )

    photos_title = models.CharField(
        "Назва розділу «Фото»",
        max_length=100,
        default="Фото",
    )

    videos_title = models.CharField(
        "Назва розділу «Відео»",
        max_length=100,
        default="Відео",
    )

    media_title = models.CharField(
        "Назва розділу «Посилання»",
        max_length=100,
        default="Посилання",
    )

    memories_title = models.CharField(
        "Назва розділу «Спогади»",
        max_length=100,
        default="Спогади",
    )

    # Головна сторінка

    home_hero_eyebrow = models.CharField(
        "Головна — текст над ім’ям",
        max_length=100,
        default="Світла пам’ять",
    )

    home_empty_title = models.CharField(
        "Головна — заголовок без біографії",
        max_length=200,
        default="Сторінка пам’яті",
    )

    home_empty_text = models.TextField(
        "Головна — текст без біографії",
        default="Інформація ще готується до публікації.",
    )

    home_life_eyebrow = models.CharField(
        "Головна — Життя: надзаголовок",
        max_length=100,
        default="Його життя",
    )

    home_life_title = models.CharField(
        "Головна — Життя: заголовок",
        max_length=200,
        default="Історія людини, яку пам’ятають",
    )

    home_life_description = models.TextField(
        "Головна — Життя: опис",
        default=(
            "Біографія, важливі дати та підтверджені родиною події — "
            "без вигаданих деталей і зайвої публічності."
        ),
    )

    home_life_empty_text = models.CharField(
        "Головна — Життя: текст порожнього стану",
        max_length=200,
        default="Хронологію ще додають.",
    )

    home_gallery_eyebrow = models.CharField(
        "Головна — Фото: надзаголовок",
        max_length=100,
        default="Фотоархів",
    )

    home_gallery_title = models.CharField(
        "Головна — Фото: заголовок",
        max_length=200,
        default="Моменти життя",
    )

    home_gallery_empty_text = models.CharField(
        "Головна — Фото: текст порожнього стану",
        max_length=200,
        default="Фотоархів ще наповнюється",
    )

    home_video_title = models.CharField(
        "Головна — Відео: заголовок без відео",
        max_length=200,
        default="Голос і живі спогади",
    )

    home_video_description = models.TextField(
        "Головна — Відео: опис без відео",
        default=(
            "Інтерв’ю, архівні записи та матеріали вшанування "
            "з короткими текстовими описами."
        ),
    )

    home_media_eyebrow = models.CharField(
        "Головна — Матеріали: надзаголовок",
        max_length=100,
        default="Публікації",
    )

    home_media_title = models.CharField(
        "Головна — Матеріали: заголовок",
        max_length=200,
        default="Матеріали та офіційні джерела",
    )

    home_media_description = models.TextField(
        "Головна — Матеріали: опис",
        default=(
            "Добірка перевірених посилань на статті, "
            "новини та офіційні документи."
        ),
    )

    # Сторінка «Життя»

    life_hero_eyebrow = models.CharField(
        "Життя — надзаголовок",
        max_length=100,
        default="Про нього",
    )

    life_hero_description = models.TextField(
        "Життя — опис",
        default=(
            "Людина поза подвигом: дитинство, навчання, родина, "
            "інтереси й підтверджена хронологія життя."
        ),
    )

    life_empty_biography_text = models.TextField(
        "Життя — текст, якщо життєпис ще не додано",
        default="Повний життєпис ще готується до публікації.",
    )

    life_empty_page_text = models.TextField(
        "Життя — текст, якщо інформація відсутня",
        default="Інформація для цієї сторінки ще готується.",
    )

    life_timeline_eyebrow = models.CharField(
        "Життя — Хронологія: надзаголовок",
        max_length=100,
        default="Хронологія",
    )

    life_timeline_title = models.CharField(
        "Життя — Хронологія: заголовок",
        max_length=200,
        default="Ключові події",
    )

    life_timeline_description = models.TextField(
        "Життя — Хронологія: опис",
        default=(
            "До публікації додаються лише події з підтвердженими "
            "датами та формулюваннями."
        ),
    )

    life_timeline_empty_title = models.CharField(
        "Життя — Хронологія: заголовок порожнього стану",
        max_length=200,
        default="Хронологія ще наповнюється",
    )

    life_timeline_empty_text = models.TextField(
        "Життя — Хронологія: текст порожнього стану",
        default=(
            "Підтверджені події з’являться тут після додавання "
            "через адміністративну панель."
        ),
    )

    life_photos_eyebrow = models.CharField(
        "Життя — Фото: надзаголовок",
        max_length=100,
        default="Фото до історії",
    )

    life_photos_title = models.CharField(
        "Життя — Фото: заголовок",
        max_length=200,
        default="Роки, що залишилися у світлинах",
    )
    # Сторінка «Подвиг і служба»

    service_section_title = models.CharField(
        "Подвиг і служба — заголовок блоку служби",
        max_length=200,
        default="Опис служби",
    )

    service_award_title = models.CharField(
        "Подвиг і служба — заголовок блоку нагороди",
        max_length=200,
        default="Нагорода",
    )

    service_safety_eyebrow = models.CharField(
        "Подвиг і служба — Безпека: надзаголовок",
        max_length=100,
        default="Безпека публікації",
    )

    service_editorial_label = models.CharField(
        "Подвиг і служба — редакційна позначка",
        max_length=150,
        default="Редакційна позначка",
    )

    service_empty_text = models.TextField(
        "Подвиг і служба — текст, якщо даних немає",
        default="Інформація для цього розділу ще не додана.",
    )

    service_decree_link_text = models.CharField(
        "Подвиг і служба — текст посилання на Указ",
        max_length=200,
        default="Читати повний текст Указу",
    )

    service_checklist_eyebrow = models.CharField(
        "Подвиг і служба — Перевірка: надзаголовок",
        max_length=100,
        default="Перед публікацією",
    )

    service_checklist_title = models.CharField(
        "Подвиг і служба — Перевірка: заголовок",
        max_length=200,
        default="Перевірка фактів і безпеки",
    )

    service_checklist_item_1 = models.CharField(
        "Подвиг і служба — Перевірка: пункт 1",
        max_length=300,
        default="Текст погоджено з частиною або пресслужбою.",
    )

    service_checklist_item_2 = models.CharField(
        "Подвиг і служба — Перевірка: пункт 2",
        max_length=300,
        default="Дата й номер Указу звірені з офіційним джерелом.",
    )

    service_checklist_item_3 = models.CharField(
        "Подвиг і служба — Перевірка: пункт 3",
        max_length=300,
        default="Немає координат, тактики, чисельності чи заборонених деталей.",
    )

    service_checklist_item_4 = models.CharField(
        "Подвиг і служба — Перевірка: пункт 4",
        max_length=300,
        default="Формулювання схвалені родиною.",
    )
    # Сторінка «Фото»

    photos_hero_title = models.CharField(
        "Фото — заголовок сторінки",
        max_length=200,
        default="Фотоархів",
    )

    photos_hero_description = models.TextField(
        "Фото — опис сторінки",
        default="Основний архів світлин, згрупований за періодами життя.",
    )

    photos_verification_note = models.TextField(
        "Фото — примітка про перевірку",
        default="Кожне фото публікується лише після перевірки.",
    )

    photos_category_empty_text = models.CharField(
        "Фото — текст порожньої категорії",
        max_length=250,
        default="У цій категорії поки немає фотографій.",
    )

    photos_empty_title = models.CharField(
        "Фото — заголовок порожнього архіву",
        max_length=200,
        default="Фотоархів ще наповнюється",
    )

    photos_empty_text = models.TextField(
        "Фото — текст порожнього архіву",
        default=(
            "Перевірені родиною фотографії з’являться тут "
            "після публікації."
        ),
    )
    # Сторінка «Відео»

    videos_hero_eyebrow = models.CharField(
        "Відео — надзаголовок",
        max_length=100,
        default="Архівні записи",
    )

    videos_hero_description = models.TextField(
        "Відео — опис сторінки",
        default=(
            "Сімейні записи, інтерв’ю, матеріали зі служби "
            "та відео вшанування."
        ),
    )

    videos_featured_label = models.CharField(
        "Відео — підпис рекомендованого відео",
        max_length=150,
        default="Рекомендоване відео",
    )

    videos_transcript_label = models.CharField(
        "Відео — заголовок текстового опису",
        max_length=150,
        default="Текстовий опис відео",
    )

    videos_all_records_label = models.CharField(
        "Відео — надзаголовок архіву",
        max_length=100,
        default="Усі записи",
    )

    videos_archive_title = models.CharField(
        "Відео — заголовок архіву",
        max_length=200,
        default="Відеоархів",
    )

    videos_admin_note = models.TextField(
        "Відео — примітка про публікацію",
        default=(
            "Усі матеріали додаються та публікуються "
            "тільки через адміністративну панель."
        ),
    )

    videos_empty_title = models.CharField(
        "Відео — заголовок порожнього архіву",
        max_length=200,
        default="Відеоархів ще наповнюється",
    )

    videos_empty_text = models.TextField(
        "Відео — текст порожнього архіву",
        default=(
            "Перевірені відеоматеріали з’являться тут "
            "після публікації адміністратором."
        ),
    )

    videos_accessibility_label = models.CharField(
        "Відео — заголовок примітки про доступність",
        max_length=100,
        default="Доступність:",
    )

    videos_accessibility_text = models.TextField(
        "Відео — текст примітки про доступність",
        default=(
            "за можливості до відео додається "
            "текстовий опис або розшифровка."
        ),
    )
    # Сторінка «Матеріали»

    media_hero_eyebrow = models.CharField(
        "Матеріали — надзаголовок",
        max_length=100,
        default="Зовнішні джерела",
    )

    media_hero_description = models.TextField(
        "Матеріали — опис сторінки",
        default=(
            "Перевірені посилання на публікації, офіційні документи "
            "й матеріали вшанування — без копіювання повних текстів."
        ),
    )

    media_section_title = models.CharField(
        "Матеріали — заголовок розділу",
        max_length=200,
        default="Матеріали",
    )

    media_verification_note = models.TextField(
        "Матеріали — примітка про перевірку посилань",
        default="Перевірка посилань рекомендована 1–2 рази на рік.",
    )

    media_empty_title = models.CharField(
        "Матеріали — заголовок порожнього стану",
        max_length=200,
        default="Матеріалів поки немає",
    )

    media_empty_text = models.TextField(
        "Матеріали — текст порожнього стану",
        default=(
            "Перевірені публікації та офіційні джерела "
            "з’являться тут пізніше."
        ),
    )
    # Сторінка «Спогади»

    memories_hero_eyebrow = models.CharField(
        "Спогади — надзаголовок",
        max_length=100,
        default="Слова близьких",
    )

    memories_hero_description = models.TextField(
        "Спогади — опис сторінки",
        default="Слова родини, побратимів, друзів і однокласників.",
    )

    memories_moderation_note = models.TextField(
        "Спогади — примітка про модерацію",
        default="Кожен текст публікується лише після ручної модерації.",
    )

    memories_empty_title = models.CharField(
        "Спогади — заголовок порожнього стану",
        max_length=200,
        default="Спогадів поки немає",
    )

    memories_empty_text = models.TextField(
        "Спогади — текст порожнього стану",
        default=(
            "Після перевірки модератором опубліковані спогади "
            "з’являться тут."
        ),
    )

    memories_submit_eyebrow = models.CharField(
        "Спогади — форма: надзаголовок",
        max_length=100,
        default="Поділитися спогадом",
    )

    memories_submit_title = models.CharField(
        "Спогади — форма: заголовок",
        max_length=200,
        default="Залиште кілька слів",
    )

    memories_submit_description = models.TextField(
        "Спогади — форма: опис",
        default=(
            "Кожне повідомлення потрапляє на ручну модерацію "
            "й не з’являється на сайті автоматично."
        ),
    )

    memories_moderation_label = models.CharField(
        "Спогади — блок модерації: заголовок",
        max_length=100,
        default="Модерація",
    )

    memories_moderator_text = models.CharField(
        "Спогади — блок модерації: відповідальна особа",
        max_length=200,
        default="Відповідальна особа від родини",
    )

    footer_text = models.TextField(
        "Текст у футері",
        blank=True,
    )

    copyright_holder = models.CharField(
        "Правовласник у копірайті",
        max_length=200,
        blank=True,
    )

    demo_strip_enabled = models.BooleanField(
        "Показувати демо-плашку",
        default=True,
        help_text=(
            "Стрічка «Демонстраційний макет» під шапкою. "
            "Вимкнути перед передачею родині."
        ),
    )

    class Meta:
        verbose_name = "Налаштування сайту"
        verbose_name_plural = "Налаштування сайту"

    def __str__(self):
        return self.site_title

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete("site_settings")

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        cached = cache.get("site_settings")
        if cached is not None:
            return cached

        obj, _ = cls.objects.get_or_create(pk=1)

        cache.set(
            "site_settings",
            obj,
            300,
        )

        return obj