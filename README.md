# Скелет шаблонів — до дня 2 з плану реалізації

## Що тут є
```
templates/
├── base.html               ← <head>, header/footer include, {% block content %}
├── includes/
│   ├── header.html          ← нав з активним пунктом, без "Контакти"
│   ├── footer.html          ← без "Контакти", динамічний рік
│   └── seo_meta.html        ← title/description/OG/Twitter з моделі SeoPage
└── pages/
    └── home.html             ← приклад: як конкретна сторінка підключається до моделей

pages/views.py                ← приклад view з реальним контекстом (Biography, Photo, Memory, SeoPage)
core/context_processors.py    ← щоб SiteSettings був доступний у header/footer на будь-якій сторінці
core/urls.py                  ← іменовані маршрути, на які посилаються {% url %} у шаблонах
```

## Що треба додати в `settings.py`, щоб це запрацювало

```python
TEMPLATES = [{
    ...
    "DIRS": [BASE_DIR / "templates"],
    "OPTIONS": {
        "context_processors": [
            "django.template.context_processors.request",   # обов'язково — header.html звіряє request.path
            "django.template.context_processors.debug",
            "django.contrib.auth.context_processors.auth",
            "django.contrib.messages.context_processors.messages",
            "core.context_processors.site_settings",         # наш, щоб не тягнути SiteSettings в кожній view
        ],
    },
}]

STATICFILES_DIRS = [BASE_DIR / "static"]
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

## Що ще треба зробити самому, за аналогією з `home.html`/`pages/views.py`

- [ ] `pages/views.py`: дописати `life`, `service`, `photos`, `videos`, `media`, `memories` за тим самим принципом — view збирає контекст → рендерить свій `pages/*.html`
- [ ] Перенести решту секцій із прототипу (`life.html`, `service.html` тощо) в `pages/*.html`, замінюючи хардкод на змінні з моделей — так само, як зроблено в `home.html`
- [ ] `favicon.ico` і `site.webmanifest`, на які посилається `seo_meta.html`, ще не створені — додати в `static/` до кінця Етапу 7
- [ ] `.hero-portrait` в `home.html` вже має логіку `{% if biography.portrait %}` / інакше `media-placeholder` — той самий патерн застосувати до `.gallery-grid` на `photos.html` і `.video-grid` на `videos.html`

## Свідомі рішення, зафіксовані в цьому скелеті

- Розділ «Контакти» відсутній і в `header.html`, і в `footer.html`, і в `core/urls.py` — узгоджено раніше, форма зворотного зв'язку лишається тільки на сторінці «Спогади»
- `prototype-toolbar` і банер «Демонстраційний макет» обгорнуті в `{% if debug %}` — не потрапляють у прод, якщо `DEBUG=False`
- `.media-placeholder` не видаляється з верстки, а лишається як fallback, коли контент ще не завантажений (`{% if photo.image %}...{% else %}...{% endif %}`)
