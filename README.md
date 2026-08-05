# Memorial

[![Django CI](https://github.com/Oleksii-Moloiko/memorial/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Oleksii-Moloiko/memorial/actions/workflows/ci.yml)

**Memorial** — вебзастосунок для створення цифрової сторінки пам’яті. Проєкт зберігає біографію, хронологію життя, фотографії, відео, згадки у медіа та спогади близьких. Контент керується через Django Admin, а публічні матеріали відображаються після публікації або модерації.

## Основні можливості

- головна сторінка з короткою біографією, хронологією та вибраними матеріалами;
- повна сторінка життєпису;
- окремий розділ про службу та подвиг;
- фотогалерея з категоріями й керованим порядком відображення;
- відеоархів із рекомендованим відео, описом, датою, тривалістю та транскриптом;
- добірка перевірених публікацій і офіційних джерел;
- форма надсилання спогадів із подальшою модерацією;
- керовані SEO-метадані для публічних сторінок;
- глобальні налаштування назви, шапки, футера та демонстраційного банера;
- адаптивна верстка, статичні та медіафайли;
- автоматичні тести, coverage і GitHub Actions CI.


## Технології

- Python 3.13
- Django 6
- PostgreSQL 16
- `uv` для залежностей і запуску команд
- Pillow для зображень
- psycopg 3 для PostgreSQL
- Docker Compose
- Nginx
- Coverage.py
- GitHub Actions

## Структура проєкту

```text
memorial/
├── apps/
│   ├── biography/       # біографія та хронологія
│   ├── core/            # глобальні налаштування сайту
│   ├── gallery/         # фотографії
│   ├── media_mentions/  # згадки у ЗМІ та офіційні джерела
│   ├── memories/        # спогади та форма надсилання
│   ├── pages/           # публічні views і URL
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
├── docker/nginx/        # конфігурація Nginx
├── static/              # вихідні статичні файли
├── media/               # локальні медіафайли
├── templates/
│   ├── includes/
│   ├── pages/
│   └── base.html
├── .github/workflows/
│   └── ci.yml
├── .coveragerc
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── pyproject.toml
└── uv.lock
```

## Публічні сторінки

| URL | Розділ |
|---|---|
| `/` | Головна |
| `/life/` | Життя |
| `/service/` | Подвиг і служба |
| `/photos/` | Фото |
| `/videos/` | Відео |
| `/media/` | У ЗМІ |
| `/memories/` | Спогади |
| `/admin/` | Django Admin |
| `/styleguide/` | Style guide, доступний лише при `DEBUG=True` |

## Швидкий запуск через Docker

### 1. Клонувати репозиторій

```bash
git clone https://github.com/Oleksii-Moloiko/memorial.git
cd memorial
```

### 2. Створити `.env`

```bash
cp .env.example .env
```

Приклад локальної конфігурації:

```env
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

DB_NAME=memorial
DB_USER=memorial
DB_PASSWORD=memorial_password
DB_HOST=db
DB_PORT=5432
```

> Файл `.env` не можна додавати в Git. Він має залишатися у `.gitignore`.

### 3. Зібрати та запустити контейнери

```bash
docker compose up --build
```

Після запуску сайт буде доступний за адресою:

```text
http://localhost:8000
```

Docker Compose автоматично:

1. запускає PostgreSQL;
2. очікує готовності бази даних;
3. застосовує міграції;
4. збирає статичні файли;
5. запускає Django;
6. віддає застосунок через Nginx.

### 4. Зупинити проєкт

```bash
docker compose down
```

Зупинити й видалити локальні volumes разом із даними PostgreSQL та завантаженими файлами:

```bash
docker compose down -v
```

> Команда з `-v` видаляє локальну базу даних і Docker volumes. Використовуйте її лише тоді, коли дані більше не потрібні.

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

Через Django Admin можна керувати такими сутностями:

- **Site settings** — назва сайту, логотип-літера, підзаголовок, футер і демонстраційний банер;
- **Biography** — ПІБ, звання, дати, портрет, вступний текст, цитата та повний життєпис;
- **Timeline events** — події хронології та порядок відображення;
- **Photos** — зображення, підпис, alt-текст, категорія, розмір картки, статус публікації та порядок;
- **Videos** — файл, обкладинка, опис, категорія, дата, тривалість, транскрипт, featured-статус і публікація;
- **Media mentions** — джерело, URL, дата й порядок;
- **Memories** — автор, роль, текст, статус модерації та featured-статус;
- **SEO pages** — title, description та Open Graph image для кожної сторінки.

Нові спогади, надіслані через публічну форму, створюються зі статусом `pending`. Вони не відображаються на сайті, доки адміністратор не змінить статус на `approved`.

## Корисні Docker-команди

### Переглянути стан контейнерів

```bash
docker compose ps
```

### Переглянути логи

```bash
docker compose logs -f
```

Логи лише Django-контейнера:

```bash
docker compose logs -f web
```

### Відкрити shell у контейнері

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

### Створити нові міграції

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

Для цього потрібні Python 3.13, `uv` і доступний PostgreSQL.

### 1. Встановити залежності

```bash
uv sync --dev
```

### 2. Налаштувати `.env`

Для PostgreSQL, запущеного локально:

```env
DB_HOST=localhost
```

### 3. Застосувати міграції

```bash
uv run python manage.py migrate
```

### 4. Запустити сервер

```bash
uv run python manage.py runserver
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

### Запустити один тест

```bash
docker compose run --rm web \
  uv run python manage.py test \
  apps.memories.tests.MemoriesPageTests.test_valid_form_creates_pending_memory \
  --verbosity=2
```

Тести покривають:

- моделі та їхні значення за замовчуванням;
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
docker compose run --rm web \
  uv run coverage erase

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

Звіт буде створено в:

```text
htmlcov/index.html
```

Файл `.coveragerc` виключає зі звіту службові файли, міграції, тести, Django Admin та environment-specific entry points, щоб показник відображав покриття основної логіки застосунку.

## Перевірки перед commit

```bash
docker compose run --rm web \
  uv run python manage.py check

docker compose run --rm web \
  uv run python manage.py makemigrations --check --dry-run

docker compose run --rm web \
  uv run python manage.py test

docker compose run --rm web \
  uv run coverage report --fail-under=90
```

## Ruff

Встановити dev-залежності локально:

```bash
uv sync --dev
```

Перевірити код:

```bash
uv run ruff check .
uv run ruff format --check .
```

Автоматично виправити доступні проблеми:

```bash
uv run ruff check . --fix
uv run ruff format .
```

## GitHub Actions CI

Workflow розташований у:

```text
.github/workflows/ci.yml
```

CI запускається для `push` і `pull_request` у гілки `main` та `develop`.

Pipeline виконує:

1. запуск PostgreSQL 16;
2. встановлення Python і `uv`;
3. встановлення залежностей із `uv.lock`;
4. `python manage.py check`;
5. перевірку відсутності незбережених міграцій;
6. застосування міграцій;
7. запуск усіх тестів із branch coverage;
8. перевірку мінімального coverage 90%.

Pull request не варто об’єднувати, якщо workflow має червоний статус.

## Змінні середовища

| Змінна | Призначення | Приклад для Docker |
|---|---|---|
| `SECRET_KEY` | секретний ключ Django | довгий випадковий рядок |
| `DEBUG` | режим розробки | `True` |
| `ALLOWED_HOSTS` | дозволені host names | `localhost,127.0.0.1` |
| `CSRF_TRUSTED_ORIGINS` | довірені origins для CSRF | `http://localhost:8000` |
| `DB_NAME` | назва PostgreSQL-бази | `memorial` |
| `DB_USER` | користувач PostgreSQL | `memorial` |
| `DB_PASSWORD` | пароль PostgreSQL | `memorial_password` |
| `DB_HOST` | адреса PostgreSQL | `db` |
| `DB_PORT` | порт PostgreSQL | `5432` |

Для GitHub Actions `DB_HOST` дорівнює `localhost`, тому що PostgreSQL service container публікує порт на runner. Для Docker Compose використовується hostname `db`.

## Налаштування production

Для production використовуйте:

```env
DJANGO_SETTINGS_MODULE=config.settings.prod
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
```

`config.settings.prod` вмикає:

- HTTPS redirect;
- secure cookies;
- HSTS;
- `ManifestStaticFilesStorage`;
- обов’язкове явне значення `ALLOWED_HOSTS`.

Перед production-запуском також потрібно:

- встановити надійний `SECRET_KEY` через секрети середовища;
- налаштувати TLS/HTTPS на reverse proxy;
- організувати резервні копії PostgreSQL і медіафайлів;
- не зберігати `.env` у репозиторії;
- розглянути object storage для великих відео й фотографій;
- налаштувати логування та моніторинг;
- запускати Django через production WSGI/ASGI server, а не `runserver`.

## Безпека файлів

Не додавайте в Git:

```text
.env
.venv/
.idea/
__pycache__/
media/*
staticfiles/
htmlcov/
.coverage
```

Якщо `.env` випадково вже потрапив у Git:

```bash
git rm --cached .env
```

Після цього потрібно змінити всі секрети, які були в цьому файлі.

## Робочий процес із Git

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

Після push створіть pull request у `develop`, дочекайтеся успішного CI та проведіть review. Перевірені зміни з `develop` об’єднуються в `main` окремим pull request.

## Поточний статус

Проєкт має робочий Docker-стек, PostgreSQL, Django Admin, автоматичні міграції, тестовий набір для основних застосунків, coverage threshold 90% і CI у GitHub Actions.

Основні наступні кроки для production-ready версії:

- object storage/CDN для медіа;
- антиспам-захист форми спогадів;
- резервне копіювання;
- production application server;
- централізоване логування та моніторинг;
- окремий deployment workflow.

## Ліцензія

Ліцензію для проєкту поки не визначено. До додавання файлу `LICENSE` усі права на код зберігаються за власником репозиторію.
