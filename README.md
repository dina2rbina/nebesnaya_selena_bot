# 🌙 Селена — персональный астролог

Telegram-бот с характером астролога. Собирает данные рождения через пошаговый wizard, сохраняет профиль в PostgreSQL и генерирует персональный натальный гороскоп через OpenRouter API.

---

## Команды бота

| Команда | Описание |
|---------|----------|
| `/start` | Приветствие и запуск онбординга (или приветствие вернувшегося пользователя) |
| `/horoscope` | Получить персональный гороскоп |
| `/profile` | Просмотреть сохранённые данные рождения |
| `/reset` | Сбросить профиль и начать заново |

---

## Структура проекта

```
bot/
├── handlers/           # Хендлеры команд и FSM
│   ├── start.py        # /start
│   ├── onboarding.py   # FSM wizard сбора данных
│   ├── profile.py      # /profile
│   ├── horoscope.py    # /horoscope
│   └── reset.py        # /reset
├── states/
│   └── onboarding.py   # FSM StatesGroup
├── models/
│   ├── base.py         # DeclarativeBase
│   └── user.py         # SQLAlchemy модель User
├── services/
│   ├── user_service.py       # CRUD пользователей
│   └── openrouter_service.py # Запросы к OpenRouter API
├── middlewares/
│   └── db.py           # Инъекция AsyncSession в хендлеры
├── keyboards/
│   └── onboarding.py   # Inline-клавиатуры
├── prompts/
│   └── selena.py       # Системный промпт персонажа + build_user_prompt()
├── config.py           # pydantic-settings конфигурация
├── database.py         # Async engine и session factory
└── main.py             # Точка входа
migrations/             # Alembic миграции
docs/
├── concept.md          # Концепция проекта
└── plan.md             # План реализации
.env.example
railway.json
Procfile
```

---

## Локальный запуск

### Требования

- Python 3.11+
- PostgreSQL 14+

### 1. Клонировать репозиторий

```bash
git clone <repo-url>
cd nebesnaya_selena_bot
```

### 2. Создать и активировать виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить переменные окружения

```bash
cp .env.example .env
```

Заполнить `.env`:

```env
BOT_TOKEN=токен_от_BotFather
OPENROUTER_API_KEY=ключ_от_openrouter.ai
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/selena_bot
LOG_LEVEL=INFO
```

### 5. Создать базу данных

```bash
createdb selena_bot  # или через psql
```

### 6. Применить миграции

```bash
alembic upgrade head
```

### 7. Запустить бота

```bash
python -m bot.main
```

---

## Деплой на Railway

### 1. Подготовка

- Форкнуть репозиторий или подключить свой
- Зарегистрироваться на [railway.com](https://railway.com)

### 2. Создать проект

1. **New Project → Deploy from GitHub repo** → выбрать репозиторий
2. **Add Plugin → PostgreSQL** — Railway автоматически создаст БД и добавит `DATABASE_URL` в переменные окружения

### 3. Добавить переменные окружения

В разделе **Variables** добавить:

| Переменная | Значение |
|-----------|---------|
| `BOT_TOKEN` | Токен от @BotFather |
| `OPENROUTER_API_KEY` | Ключ от openrouter.ai |
| `OPENROUTER_MODEL` | `mistralai/mistral-7b-instruct` |
| `LOG_LEVEL` | `INFO` |

> `DATABASE_URL` Railway подставляет автоматически из PostgreSQL плагина.

### 4. Деплой

Происходит автоматически при пуше в ветку. При старте выполняется:

```
alembic upgrade head && python -m bot.main
```

---

## Переменные окружения

| Переменная | Обязательная | Описание |
|-----------|:---:|---------|
| `BOT_TOKEN` | ✅ | Telegram Bot Token от @BotFather |
| `OPENROUTER_API_KEY` | ✅ | API ключ от openrouter.ai |
| `DATABASE_URL` | ✅ | `postgresql+asyncpg://user:pass@host:port/db` |
| `OPENROUTER_MODEL` | — | Модель (по умолчанию: `mistralai/mistral-7b-instruct`) |
| `LOG_LEVEL` | — | Уровень логов (по умолчанию: `INFO`) |

---

## Технологический стек

| Компонент | Технология |
|-----------|-----------|
| Bot framework | Aiogram 3 |
| База данных | PostgreSQL + asyncpg |
| ORM | SQLAlchemy 2.x (async) |
| Миграции | Alembic |
| AI API | OpenRouter API (aiohttp) |
| Конфигурация | pydantic-settings |
| Деплой | Railway.com |
