# Memorial

[![Django CI](https://github.com/Oleksii-Moloiko/memorial/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/Oleksii-Moloiko/memorial/actions/workflows/ci.yml)

**Memorial** — Django-вебзастосунок для створення цифрової сторінки пам’яті. Проєкт зберігає біографію, хронологію життя, матеріали про службу та нагороди, фотографії, відео, згадки у медіа й спогади близьких. Контент керується через Django Admin, а публічні матеріали відображаються лише після публікації або модерації.

Проєкт підтримує українську як основну мову та англійські версії контентних полів через `django-modeltranslation`.

## Основні можливості

- головна сторінка з короткою біографією, хронологією та вибраними матеріалами;
- повна сторінка життєпису;
- окремий розділ про службу, подвиг, нагороди, цитати та пов’язані джерела;
- фотогалерея з категоріями й керованим порядком відображення;
- відеоархів із featured-відео, описом, датою, тривалістю та транскриптом;
- добірка перевірених публікацій і офіційних джерел;
- форма надсилання спогадів із модерацією, honeypot-полем і rate limit;
- керовані SEO-метадані для публічних сторінок;
- глобальні налаштування текстів сайту, шапки, футера, empty states та допоміжного контенту;
- українські та англійські версії контентних полів у Django Admin;
- локалізовані URL для публічних сторінок: українська без префікса, англійська з `/en/`;
- адаптивна верстка, статичні та медіафайли;
- Docker Compose стек із PostgreSQL, Gunicorn і Nginx;
- production-конфігурація з WhiteNoise та окремим deploy-скриптом;
- автоматичні тести, branch coverage, Ruff і GitHub Actions CI.

## Технології

- Python 3.13
- Django 6
- PostgreSQL 16
- `uv` для керування залежностями та локального запуску команд
- `django-environ` для змінних середовища
- `django-modeltranslation` для перекладу контентних полів
- `django-ratelimit` для обмеження повторних POST-запитів
- Pillow для зображень
- psycopg 3 для PostgreSQL
- Gunicorn
- WhiteNoise
- Docker Compose
- Nginx
- Ruff
- Coverage.py
- GitHub Actions

## Структура проєкту

```text
memorial/
├── apps/
│   ├── biography/       # біографія та хронологія
│   ├── core/            # глобальні налаштування сайту та admin helpers
│   ├── gallery/         # фотографії
│   ├── media_mentions/  # згадки у ЗМІ та офіційні джерела
│   ├── memories/        # спогади та форма надсилання
│   ├── pages/           # публічні views, URL і контент сторінок
│   ├── seo/             # SEO-налаштування сторінок
│   └── videos/          # відеоархів
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   └── prod.py
│   ├── context_processors.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── docker/nginx/        # конфігурація Nginx для Docker
├── media/               # локальні медіафайли
├── static/              # вихідні статичні файли
├── templates/           # публічні та admin-шаблони
├── .github/workflows/
│   └── ci.yml
├── .coveragerc
├── .env.example
├── deploy.sh            # production deployment з гілки develop
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── pyproject.toml
├── requirements.txt     # production export із uv.lock
├── server.py            # Gunicorn entry point для hosting environment
└── uv.lock
```

У застосунках, контент яких перекладається, є `translation.py` з реєстрацією полів для `django-modeltranslation`.

## Публічні сторінки

Українська — основна мова й не має мовного префікса:

| URL | Розділ |
|---|---|
| `/` | Головна |
| `/life/` | Життя |
| `/service/` | Подвиг і служба |
| `/photos/` | Фото |
| `/videos/` | Відео |
| `/media/` | Redirect до секції джерел на сторінці служби |
| `/memories/` | Спогади |
| `/admin/` | Django Admin |
| `/admin/home/` | Кастомна головна сторінка Admin |
| `/styleguide/` | Style guide, лише при `DEBUG=True` |

Для англійської версії публічних URL Django додає префікс `/en/`, наприклад:

```text
/en/
/en/life/
/en/service/
/en/photos/
/en/videos/
/en/memories/
```

Endpoint `/i18n/setlang/` використовується Django для перемикання активної мови.

> Локалізація через `django-modeltranslation` стосується зареєстрованих контентних полів моделей. Якщо додається нове текстове поле, яке має бути двомовним, його потрібно також зареєструвати у відповідному `translation.py` і створити міграцію.

## Швидкий запуск через Docker

Docker Compose використовує `config.settings.prod`. Для локального запуску через HTTP потрібно явно залишити `SECURE_SSL_REDIRECT=False` і HSTS-властивості вимкненими, як у прикладі нижче.

### 1. Клонувати репозиторій

```bash
git clone https://github.com/Oleksii-Moloiko/memorial.git
cd memorial
```

Для актуальної робочої версії:

```bash
git checkout develop
```

### 2. Створити `.env`

```bash
cp .env.example .env
```

Для локального Docker-запуску змініть значення на локальні, наприклад:

```env
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=False

ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

DB_NAME=memorial
DB_USER=memorial
DB_PASSWORD=memorial_password
DB_HOST=db
DB_PORT=5432

SECURE_SSL_REDIRECT=False
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
```

> `.env` не можна додавати в Git. Файл уже виключений через `.gitignore`.

### 3. Зібрати та запустити контейнери

```bash
docker compose up --build
```

Після запуску сайт буде доступний за адресою:

```text
http://localhost:8000
```

Docker Compose автоматично:

1. запускає PostgreSQL 16;
2. очікує готовності бази даних;
3. застосовує міграції;
4. збирає статичні файли;
5. запускає Django через Gunicorn;
6. віддає застосунок, `/static/` і `/media/` через Nginx.

Nginx у Docker дозволяє request body до `320M`, що важливо для завантаження великих медіафайлів.

### 4. Зупинити проєкт

```bash
docker compose down
```

Зупинити й видалити локальні Docker volumes разом із PostgreSQL та завантаженими медіафайлами:

```bash
docker compose down -v
```

> `docker compose down -v` видаляє локальні дані. Використовуйте команду лише тоді, коли вони більше не потрібні.

## Створення адміністратора

Коли контейнери запущені:

```bash
docker compose exec web \
  uv run python manage.py createsuperuser
```

Або через одноразовий контейнер:

```bash
docker compose run --rm web \
  uv run python manage.py createsuperuser
```

Після цього відкрийте:

```text
http://localhost:8000/admin/
```

## Керування контентом

Через Django Admin можна керувати основними сутностями проєкту:

- **Site settings** — глобальні тексти, брендинг, footer, empty states та інший керований контент;
- **Biography** — ПІБ, звання, дати, портрет, вступний текст, цитата та повний життєпис;
- **Timeline events** — події хронології та порядок відображення;
- **Service page / awards / quotes** — контент сторінки служби, нагороди, цитати та джерела;
- **Photos** — зображення, caption, alt-текст, категорія, розмір картки, статус публікації та порядок;
- **Videos** — файл, обкладинка, опис, категорія, дата, тривалість, транскрипт, featured-статус і публікація;
- **Media mentions** — назва матеріалу, джерело, URL, дата, featured-статус і порядок;
- **Memories** — автор, роль, текст, статус модерації та featured-статус;
- **SEO pages** — title, description та Open Graph image для публічних сторінок.

Для моделей із локалізованими полями Django Admin показує окремі українські та англійські значення.

Нові спогади, надіслані через публічну форму, створюються зі статусом `pending` і `featured=False`. Вони не відображаються на сайті, доки адміністратор не змінить статус на `approved`.

Форма додатково має:

- honeypot-поле проти простих ботів;
- серверну валідацію;
- rate limit `3 POST / hour / IP`;
- JSON-відповідь для AJAX submit;
- HTTP `429` при перевищенні ліміту.

## Корисні Docker-команди

### Стан контейнерів

```bash
docker compose ps
```

### Логи

```bash
docker compose logs -f
```

Лише Django/Gunicorn:

```bash
docker compose logs -f web
```

### Shell у контейнері

```bash
docker compose exec web sh
```

### Django shell

```bash
docker compose exec web \
  uv run python manage.py shell
```

### Застосувати міграції

```bash
docker compose exec web \
  uv run python manage.py migrate
```

### Створити міграції

```bash
docker compose exec web \
  uv run python manage.py makemigrations
```

### Зібрати статичні файли

```bash
docker compose exec web \
  uv run python manage.py collectstatic --noinput
```

## Локальний запуск без Docker

Потрібні Python 3.13, `uv` і доступний PostgreSQL.

### 1. Встановити залежності

```bash
uv sync --dev
```

### 2. Створити `.env`

```bash
cp .env.example .env
```

Для PostgreSQL, запущеного локально:

```env
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

DB_NAME=memorial
DB_USER=memorial
DB_PASSWORD=memorial_password
DB_HOST=localhost
DB_PORT=5432
```

### 3. Застосувати міграції

```bash
uv run python manage.py migrate
```

### 4. Запустити dev server

```bash
uv run python manage.py runserver
```

`manage.py` використовує `config.settings.dev` за замовчуванням, тому локальний `runserver` запускається в development-конфігурації.

Після запуску:

```text
http://127.0.0.1:8000/
```

Style guide у dev-режимі:

```text
http://127.0.0.1:8000/styleguide/
```

## Тести

Проєкт використовує стандартний Django test runner.

### Запустити всі тести через Docker

```bash
docker compose run --rm web \
  uv run python manage.py test --verbosity=2
```

### Запустити тести окремого застосунку

```bash
docker compose run --rm web \
  uv run python manage.py test apps.memories --verbosity=2
```

### Запустити конкретний клас

```bash
docker compose run --rm web \
  uv run python manage.py test \
  apps.memories.tests.MemoryFormTests \
  --verbosity=2
```

Тести перевіряють, зокрема:

- моделі та значення за замовчуванням;
- порядок сортування записів;
- форми й валідацію;
- публічні views і шаблони;
- фільтрацію неопублікованого контенту;
- модерацію спогадів;
- відеовалідатори;
- глобальні налаштування сайту;
- SEO-контекст і метатеги;
- порожні стани сторінок.

## Coverage

### Побудувати coverage-звіт

```bash
docker compose run --rm web uv run coverage erase

docker compose run --rm web \
  uv run coverage run --branch manage.py test

docker compose run --rm web \
  uv run coverage report -m
```

### Перевірити мінімальний поріг

```bash
docker compose run --rm web \
  uv run coverage report --fail-under=90
```

### Створити HTML-звіт

```bash
docker compose run --rm web \
  uv run coverage html
```

Результат:

```text
htmlcov/index.html
```

`.coveragerc` виключає зі звіту службові файли, міграції, тести, Django Admin та environment-specific entry points, щоб coverage відображав покриття основної логіки застосунку.

## Ruff

Встановити dev-залежності:

```bash
uv sync --dev
```

Перевірити lint і форматування:

```bash
uv run ruff check .
uv run ruff format --check .
```

Автоматично виправити доступні проблеми:

```bash
uv run ruff check . --fix
uv run ruff format .
```

## Перевірки перед commit

Рекомендований локальний набір перевірок:

```bash
uv run ruff check .
uv run ruff format --check .
uv run python manage.py check
uv run python manage.py makemigrations --check --dry-run
uv run coverage run --branch manage.py test --verbosity=2
uv run coverage report --fail-under=90
```

## GitHub Actions CI

Workflow:

```text
.github/workflows/ci.yml
```

CI запускається для `push` і `pull_request` у гілки `main` та `develop`.

Pipeline виконує:

1. запуск PostgreSQL 16;
2. встановлення `uv` і Python із `.python-version`;
3. `uv sync --locked --dev`;
4. `ruff check .`;
5. `ruff format --check .`;
6. `python manage.py check`;
7. перевірку відсутності незбережених міграцій;
8. застосування міграцій;
9. запуск тестів із branch coverage;
10. перевірку мінімального coverage `90%`.

Pull request не варто об’єднувати, якщо workflow має червоний статус.

## Змінні середовища

| Змінна | Призначення | Типовий Docker local |
|---|---|---|
| `SECRET_KEY` | секретний ключ Django | довгий випадковий рядок |
| `DEBUG` | базове значення debug | `False` |
| `ALLOWED_HOSTS` | дозволені host names | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | довірені origins для CSRF | `http://localhost:8000` |
| `DB_NAME` | назва PostgreSQL-бази | `memorial` |
| `DB_USER` | користувач PostgreSQL | `memorial` |
| `DB_PASSWORD` | пароль PostgreSQL | `memorial_password` |
| `DB_HOST` | адреса PostgreSQL | `db` |
| `DB_PORT` | порт PostgreSQL | `5432` |
| `SECURE_SSL_REDIRECT` | redirect HTTP → HTTPS у prod | `False` локально |
| `SECURE_HSTS_SECONDS` | HSTS max-age | `0` локально |
| `SECURE_HSTS_INCLUDE_SUBDOMAINS` | HSTS для subdomains | `False` локально |
| `SECURE_HSTS_PRELOAD` | HSTS preload flag | `False` локально |

Для GitHub Actions `DB_HOST=localhost`, тому що PostgreSQL service container публікує порт на runner. Для Docker Compose використовується hostname `db`.

## Production settings

Production settings:

```text
config.settings.prod
```

Ключові властивості production-конфігурації:

- `DEBUG=False` примусово;
- `ALLOWED_HOSTS` має бути явно заданий;
- HTTPS redirect керується через `SECURE_SSL_REDIRECT`;
- secure session і CSRF cookies;
- HSTS керується environment variables;
- `SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")`;
- статичні файли використовують `WhiteNoise` + `CompressedManifestStaticFilesStorage`;
- media залишаються у filesystem storage;
- застосунок запускається через Gunicorn.

Приклад production `.env`:

```env
SECRET_KEY=replace-with-a-production-secret
DEBUG=False

ALLOWED_HOSTS=example.com,www.example.com
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com

DB_NAME=memorial
DB_USER=memorial
DB_PASSWORD=replace-with-a-strong-password
DB_HOST=localhost
DB_PORT=5432

SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=0
SECURE_HSTS_INCLUDE_SUBDOMAINS=False
SECURE_HSTS_PRELOAD=False
```

> Увімкнення великого `SECURE_HSTS_SECONDS`, `SECURE_HSTS_INCLUDE_SUBDOMAINS=True` або `SECURE_HSTS_PRELOAD=True` потрібно робити лише після того, як HTTPS стабільно працює на всіх потрібних доменах і піддоменах.

## Production deployment через `deploy.sh`

У репозиторії є deploy-скрипт для поточного server/ISPmanager flow:

```text
./deploy.sh
```

Скрипт розрахований на такі умови:

- активна гілка — `develop`;
- working tree чистий;
- virtual environment уже існує в `./.venv`;
- production `.env` уже налаштований;
- PostgreSQL доступний за параметрами з `.env`;
- користувач має право виконувати `git pull` і змінювати файли проєкту.

Запуск:

```bash
./deploy.sh
```

`deploy.sh` послідовно:

1. перевіряє активну гілку;
2. зупиняється, якщо є незакомічені зміни;
3. виконує `git pull --ff-only origin develop`;
4. оновлює production dependencies із `requirements.txt`;
5. запускає Django system check;
6. перевіряє відсутність missing migrations;
7. застосовує міграції;
8. виконує `collectstatic`;
9. просить вручну перезапустити Python application в ISPmanager.

Скрипт **не** створює `.venv`, **не** створює `.env`, **не** робить backup бази й **не** перезапускає application process автоматично.

### Початкова підготовка virtual environment на сервері

Один раз до першого deploy:

```bash
python3.13 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
```

Після цього налаштуйте `.env`, перевірте production settings і виконайте початкові міграції/collectstatic або запустіть `deploy.sh`, якщо repository state відповідає його вимогам.

## `requirements.txt` і `uv.lock`

`uv.lock` — основний lock-файл проєкту.

`requirements.txt` потрібен для production-середовища, де dependencies встановлюються через `pip`. Він генерується з `uv.lock` і не повинен редагуватися вручну.

Оновити export після зміни production dependencies:

```bash
uv export \
  --frozen \
  --no-dev \
  --no-emit-project \
  --format requirements.txt \
  --output-file requirements.txt
```

Після зміни dependencies варто закомітити разом:

```text
pyproject.toml
uv.lock
requirements.txt
```

## Статичні та медіафайли

### Static

- source: `static/`;
- collect destination: `staticfiles/`;
- production storage: `CompressedManifestStaticFilesStorage`;
- у Docker `/static/` віддає Nginx;
- у direct production deployment WhiteNoise підключений у middleware і готовий обслуговувати зібрані static assets.

### Media

- локальна директорія: `media/`;
- `media/*` виключено з Git;
- `media/.gitkeep` залишає директорію в репозиторії;
- у Docker media зберігаються в окремому volume й віддаються Nginx;
- у production використовується filesystem storage.

Для production потрібно окремо організувати backup медіафайлів. Для великих обсягів фотографій/відео варто розглянути object storage/CDN.

## Безпека файлів і секретів

Не додавайте в Git:

```text
.env
.venv/
.idea/
.vscode/
__pycache__/
media/*
staticfiles/
htmlcov/
.coverage
.pytest_cache/
.ruff_cache/
```

Якщо `.env` випадково вже потрапив у Git:

```bash
git rm --cached .env
```

Після цього потрібно змінити всі секрети, які містилися у файлі.

## Робочий процес із Git

Поточний deployment script працює з `develop`, а CI перевіряє `develop` і `main`.

Рекомендована схема:

```text
feature/* → develop → main
```

Приклад:

```bash
git checkout develop
git pull
git checkout -b feature/add-content-section

# зміни

git add .
git commit -m "Add content section"
git push -u origin feature/add-content-section
```

Після push створіть pull request у `develop`, дочекайтеся успішного CI та review. Злиття в `main` виконуйте окремим pull request, коли версію готово зафіксувати як стабільну.

## Поточний статус

На поточному етапі проєкт має:

- Django 6 + PostgreSQL 16;
- робочий Docker Compose стек;
- Gunicorn і Nginx;
- production settings з WhiteNoise;
- Django Admin для керування контентом;
- українські та англійські поля контенту через `django-modeltranslation`;
- модерацію та базовий антиспам для форми спогадів;
- тестовий набір для основних застосунків;
- branch coverage threshold `90%`;
- Ruff lint/format checks;
- GitHub Actions CI;
- production dependency export у `requirements.txt`;
- deploy-скрипт для поточного ISPmanager workflow.

Що ще варто закрити для більш зрілого production setup:

- автоматизовані резервні копії PostgreSQL та media;
- object storage/CDN для великих media assets;
- централізоване логування та error monitoring;
- автоматичний restart/deploy workflow замість ручного restart у hosting panel;
- health check/uptime monitoring;
- повна локалізація всіх системних та form-повідомлень, якщо англомовний UI має бути повністю самодостатнім.

## Ліцензія

Ліцензію для проєкту поки не визначено. До додавання файлу `LICENSE` усі права на код зберігаються за власником репозиторію.
