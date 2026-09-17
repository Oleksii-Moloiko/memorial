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

    memories_title = models.CharField(
        "Назва розділу «Спогади»",
        max_length=100,
        default="Спогади",
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
        default=("Після перевірки модератором опубліковані спогади з’являться тут."),
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

    memories_submit_button_label = models.CharField(
        "Спогади — форма: текст кнопки надсилання",
        max_length=200,
        default="Надіслати на модерацію",
    )

    memories_success_message = models.TextField(
        "Спогади — повідомлення про успішне надсилання",
        default="Дякуємо. Ваш спогад надіслано на модерацію.",
    )

    memories_error_message = models.TextField(
        "Спогади — повідомлення про помилку надсилання",
        default="Щось пішло не так. Перевірте дані у формі та спробуйте ще раз.",
        help_text="Також показується при проблемах зі з’єднанням. Введені дані зберігаються у формі.",
    )

    memories_rate_limit_message = models.TextField(
        "Спогади — повідомлення про ліміт надсилань",
        default=(
            "Ви надіслали кілька спогадів за короткий час. "
            "Спробуйте, будь ласка, пізніше."
        ),
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

    memories_name_label = models.TextField(
        "Спогади — підпис поля імені", default="Ім’я або підпис"
    )

    memories_name_placeholder = models.TextField(
        "Спогади — приклад імені", default="Наприклад: Іван або позивний «Сокіл»"
    )

    memories_category_label = models.TextField(
        "Спогади — підпис категорії", default="Ким ви були знайомі"
    )

    memories_category_placeholder = models.TextField(
        "Спогади — порожня категорія", default="Оберіть варіант"
    )

    memories_text_label = models.TextField(
        "Спогади — підпис тексту", default="Текст спогаду"
    )

    memories_text_placeholder = models.TextField(
        "Спогади — підказка тексту", default="Напишіть спогад"
    )

    memories_text_hint = models.TextField(
        "Спогади — пояснення скорочення",
        default="Довгі спогади у стрічці показуються скорочено — повний текст відкривається кнопкою «Дивитись більше».",
    )

    memories_consent_label = models.TextField(
        "Спогади — згода",
        default="Погоджуюся на публікацію після перевірки модератором.",
    )

    memories_more_label = models.TextField(
        "Спогади — кнопка розгортання", default="Дивитись більше"
    )

    memories_limit_message = models.TextField(
        "Спогади — ліміт тексту",
        default="Досягнуто ліміт в 15 000 символів. Надішліть цей спогад, а продовження — ще однією формою.",
    )

    memories_name_error = models.TextField(
        "Спогади — коротке ім’я",
        default="Вкажіть ім’я або підпис щонайменше з двох символів.",
    )

    memories_text_error = models.TextField(
        "Спогади — короткий текст", default="Спогад має містити щонайменше 10 символів."
    )

    memories_required_error = models.TextField(
        "Спогади — обов’язкове поле", default="Це поле обов’язкове."
    )

    memories_invalid_error = models.TextField(
        "Спогади — помилка поля", default="Перевірте це поле."
    )

    memories_close_label = models.TextField("Спогади — закриття", default="Закрити")

    memories_close_dialog_label = models.TextField(
        "Спогади — закриття діалогу", default="Закрити спогад"
    )

    memories_characters_label = models.TextField(
        "Спогади — одиниця лічильника", default="символів"
    )

    memories_escape_label = models.TextField(
        "Спогади — підказка клавіші", default="Esc — закрити"
    )

    footer_dedication = models.TextField(
        "Футер — пам’ятний напис",
        default="Сторінка розроблена в світлу пам’ять Назара Боровицького",
    )

    language_label = models.TextField("Хедер — мова", default="Мова")

    mobile_language_label = models.TextField(
        "Хедер — мова в мобільному меню", default="МОВА / LANGUAGE"
    )

    photos_all_label = models.TextField("Фото — всі категорії", default="Усі фото")

    videos_date_label = models.TextField("Відео — дата", default="Дата запису")

    videos_category_label = models.TextField("Відео — категорія", default="Категорія")

    videos_duration_label = models.TextField("Відео — тривалість", default="Тривалість")

    demo_title = models.TextField("Демо — заголовок", default="Демонстраційний макет.")

    demo_text = models.TextField(
        "Демо — пояснення",
        default="Усі персональні дані та матеріали умовні й мають бути замінені після перевірки родиною.",
    )

    photo_category_family = models.TextField(
        "Фото — назва категорії «Сім’я та дитинство»", default="Сім’я та дитинство"
    )

    photo_category_study = models.TextField(
        "Фото — назва категорії «Навчання»", default="Навчання"
    )

    photo_category_service = models.TextField(
        "Фото — назва категорії «Служба та побратими»", default="Служба та побратими"
    )

    photo_category_memory = models.TextField(
        "Фото — назва категорії «Вшанування»", default="Вшанування"
    )

    video_category_family = models.TextField(
        "Відео — назва категорії «Сімейний архів»", default="Сімейний архів"
    )

    video_category_interview = models.TextField(
        "Відео — назва категорії «Інтерв’ю»", default="Інтерв’ю"
    )

    video_category_service = models.TextField(
        "Відео — назва категорії «Служба»", default="Служба"
    )

    video_category_memory = models.TextField(
        "Відео — назва категорії «Вшанування»", default="Вшанування"
    )

    video_category_media = models.TextField(
        "Відео — назва категорії «Матеріали ЗМІ»", default="Матеріали ЗМІ"
    )

    video_category_other = models.TextField(
        "Відео — назва категорії «Інше»", default="Інше"
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
