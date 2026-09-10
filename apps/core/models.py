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
