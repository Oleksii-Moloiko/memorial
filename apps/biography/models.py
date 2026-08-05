from django.db import models


class Biography(models.Model):
    """Життєпис. Singleton (одна людина = один сайт)."""

    full_name = models.CharField("ПІБ", max_length=255)
    rank = models.CharField(
        "Звання / роль",
        max_length=255,
        blank=True,
        help_text="Наприклад: «Старший лейтенант, командир взводу»",
    )
    birth_date = models.DateField("Дата народження", null=True, blank=True)
    death_date = models.DateField("Дата смерті", null=True, blank=True)
    portrait = models.ImageField(
        "Портрет", upload_to="biography/", null=True, blank=True
    )
    award_title = models.CharField(
        "Нагорода (коротко)",
        max_length=255,
        blank=True,
        help_text="Наприклад: «Герой України»",
    )
    intro_text = models.TextField("Вступний текст на головній", blank=True)
    signature_quote = models.CharField("Ключова цитата", max_length=500, blank=True)
    summary = models.TextField("Короткий опис (для головної)", blank=True)
    full_text = models.TextField("Повний життєпис", blank=True)

    class Meta:
        verbose_name = "Життєпис"
        verbose_name_plural = "Життєпис"

    def __str__(self):
        return self.full_name


class TimelineEvent(models.Model):
    """Подія хронології життя. date_label — текст, не строга дата
    (в макеті трапляються діапазони на кшталт «2001–2011»)."""

    date_label = models.CharField("Дата / період", max_length=50)
    title = models.CharField("Заголовок події", max_length=255)
    description = models.CharField("Опис", max_length=500, blank=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Подія хронології"
        verbose_name_plural = "Хронологія"
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.date_label} — {self.title}"
