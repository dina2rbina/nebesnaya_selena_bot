# План реализации: Telegram-бот «Селена»

## Этапы реализации

---

## Этап 1: Инициализация проекта и конфигурация

### Задачи:
1. Создать структуру директорий проекта (`bot/`, `bot/handlers/`, `bot/states/`, `bot/models/`, `bot/services/`, `bot/keyboards/`, `bot/prompts/`, `migrations/`)
2. Создать `requirements.txt` со всеми зависимостями:
   - `aiogram==3.x`
   - `asyncpg`
   - `sqlalchemy[asyncio]`
   - `alembic`
   - `pydantic-settings`
   - `aiohttp` (для OpenRouter)
   - `python-dotenv`
3. Создать `bot/config.py` с pydantic-settings: BOT_TOKEN, OPENROUTER_API_KEY, OPENROUTER_MODEL, DATABASE_URL, LOG_LEVEL
4. Создать `.env.example` с пустыми значениями и комментариями
5. Создать `bot/__init__.py` и пустые `__init__.py` во всех подпакетах
6. Настроить логирование в `bot/config.py` или отдельном `bot/logging_config.py`

### Ожидаемый результат:
- Чистая структура проекта
- Конфигурация читается из `.env` через pydantic-settings
- `python -c "from bot.config import settings; print(settings)"` работает без ошибок

---

## Этап 2: База данных — модели и миграции

### Задачи:
1. Создать `bot/models/user.py` — SQLAlchemy модель `User`:
   - `id` (Integer, PK, autoincrement)
   - `telegram_id` (BigInteger, unique, not null, indexed)
   - `name` (String(100), not null)
   - `birth_date` (String(20), not null) — хранить как строку формата «ДД.ММ.ГГГГ»
   - `birth_time` (String(10), nullable) — «ЧЧ:ММ» или NULL если не указано
   - `birth_place` (String(200), not null)
   - `created_at` (DateTime, default=now)
2. Создать `bot/models/base.py` с `DeclarativeBase`
3. Создать `bot/models/__init__.py`
4. Инициализировать Alembic: `alembic init migrations`
5. Настроить `alembic.ini` и `migrations/env.py` для async + SQLAlchemy
6. Создать первую миграцию: `alembic revision --autogenerate -m "create users table"`
7. Создать `bot/database.py` — async engine, session factory, функция `get_session()`

### Ожидаемый результат:
- Модель описана корректно
- `alembic upgrade head` применяет миграцию без ошибок
- Таблица `users` создана в БД

---

## Этап 3: Сервисный слой — работа с пользователями

### Задачи:
1. Создать `bot/services/user_service.py`:
   - `get_user_by_telegram_id(session, telegram_id) → User | None`
   - `create_user(session, telegram_id, name, birth_date, birth_time, birth_place) → User`
   - `update_user(session, telegram_id, **kwargs) → User`
   - `delete_user(session, telegram_id) → bool`
2. Все функции — async, принимают AsyncSession
3. Добавить обработку исключений (IntegrityError при дублировании)

### Ожидаемый результат:
- CRUD операции для пользователя работают корректно
- Нет синхронных блокирующих вызовов

---

## Этап 4: Системный промпт Селены

### Задачи:
1. Создать `bot/prompts/selena.py` с константой `SELENA_SYSTEM_PROMPT`
2. Создать `bot/prompts/__init__.py`
3. Промпт включает: портрет аудитории, структуру ответа БОЛЬ→ПОНИМАНИЕ→ОБЪЯСНЕНИЕ→НАДЕЖДА→ДЕЙСТВИЕ, языковые принципы, примеры фраз
4. Создать функцию `build_user_prompt(name, birth_date, birth_time, birth_place) → str` — формирует конкретный запрос с данными пользователя

### Ожидаемый результат:
- Промпт импортируется без ошибок
- `build_user_prompt(...)` возвращает корректную строку с данными пользователя

---

## Этап 5: Сервис OpenRouter API

### Задачи:
1. Создать `bot/services/openrouter_service.py`:
   - Класс `OpenRouterService` или набор функций
   - `generate_horoscope(name, birth_date, birth_time, birth_place) → str`
   - POST запрос к `https://openrouter.ai/api/v1/chat/completions`
   - Заголовки: `Authorization: Bearer {key}`, `Content-Type: application/json`
   - Body: `{"model": settings.OPENROUTER_MODEL, "messages": [{"role": "system", ...}, {"role": "user", ...}]}`
   - Таймаут: 60 секунд
2. Обработка ошибок:
   - Таймаут → понятное сообщение пользователю
   - HTTP 4xx/5xx → логирование + сообщение пользователю
   - Парсинг ответа с защитой от unexpected structure

### Ожидаемый результат:
- Функция возвращает текст гороскопа или бросает понятное исключение
- Ошибки API не крашат бота

---

## Этап 6: FSM States и клавиатуры

### Задачи:
1. Создать `bot/states/onboarding.py` — `OnboardingStates(StatesGroup)`:
   - `waiting_for_name`
   - `waiting_for_birth_date`
   - `waiting_for_birth_time`
   - `waiting_for_birth_place`
2. Создать `bot/keyboards/onboarding.py`:
   - Inline-кнопка «Пропустить» для времени рождения (оно необязательно)
   - Reply-клавиатура или inline для подтверждения данных
3. Создать `bot/keyboards/__init__.py`

### Ожидаемый результат:
- States и клавиатуры импортируются без ошибок
- Структура FSM корректна для Aiogram 3

---

## Этап 7: Хендлеры команд и FSM

### Задачи:
1. Создать `bot/handlers/start.py`:
   - `/start` — проверяет существующего пользователя. Если есть → приветствует по имени, предлагает `/horoscope`. Если нет → запускает онбординг
2. Создать `bot/handlers/onboarding.py` — FSM wizard:
   - Шаг 1: запрос имени (`waiting_for_name`) → валидация (не пустое, не слишком длинное)
   - Шаг 2: запрос даты рождения (`waiting_for_birth_date`) → валидация формата ДД.ММ.ГГГГ
   - Шаг 3: запрос времени рождения (`waiting_for_birth_time`) → кнопка «Не знаю» / валидация ЧЧ:ММ
   - Шаг 4: запрос места рождения (`waiting_for_birth_place`) → сохранение в БД → подтверждение
3. Создать `bot/handlers/profile.py`:
   - `/profile` — выводит сохранённые данные пользователя
   - Если профиля нет → предлагает пройти онбординг
4. Создать `bot/handlers/horoscope.py`:
   - `/horoscope` — если нет профиля → онбординг. Если есть → вызывает OpenRouter, отправляет ответ
   - Показывает «typing...» пока генерируется гороскоп
5. Создать `bot/handlers/reset.py`:
   - `/reset` — запрашивает подтверждение, удаляет профиль из БД
6. Создать `bot/handlers/__init__.py` с функцией `register_all_handlers(dp: Dispatcher)`

### Ожидаемый результат:
- Все команды работают корректно
- FSM переходит между состояниями без ошибок
- Некорректный ввод обрабатывается с понятным сообщением

---

## Этап 8: Точка входа и запуск бота

### Задачи:
1. Создать `bot/main.py`:
   - Инициализация бота (`Bot`) и диспетчера (`Dispatcher`)
   - Подключение хендлеров через `register_all_handlers(dp)`
   - Инициализация пула БД при старте (создать engine, проверить подключение)
   - Запуск `dp.start_polling(bot)`
   - Graceful shutdown (закрыть сессии БД при остановке)
2. Передача `AsyncSession` в хендлеры через middleware или FSM context
3. Тестовый запуск без реальных credentials (проверить импорты)

### Ожидаемый результат:
- `python -m bot.main` запускает бота
- Бот отвечает на `/start`

---

## Этап 9: Конфигурация деплоя

### Задачи:
1. Создать `Procfile`:
   ```
   web: python -m bot.main
   ```
2. Создать `railway.json`:
   ```json
   {
     "$schema": "https://railway.app/railway.schema.json",
     "build": { "builder": "nixpacks" },
     "deploy": { "startCommand": "alembic upgrade head && python -m bot.main", "restartPolicyType": "ON_FAILURE" }
   }
   ```
3. Проверить `.gitignore` (`.env` должен быть исключён)
4. Финальная проверка `requirements.txt`

### Ожидаемый результат:
- `railway.json` и `Procfile` готовы для деплоя
- Миграции применяются автоматически при деплое

---

## Этап 10: README и финальная документация

### Задачи:
1. Создать `README.md`:
   - Описание проекта и персонажа Селены
   - Скриншот/демо (placeholder)
   - Требования (Python 3.11+, PostgreSQL)
   - Инструкция локального запуска:
     1. Клонировать репозиторий
     2. Создать `.env` из `.env.example`
     3. Установить зависимости: `pip install -r requirements.txt`
     4. Применить миграции: `alembic upgrade head`
     5. Запустить: `python -m bot.main`
   - Инструкция деплоя на Railway:
     1. Fork репозитория
     2. Создать проект на railway.com
     3. Подключить репозиторий
     4. Добавить PostgreSQL плагин
     5. Установить переменные окружения
     6. Деплой происходит автоматически
   - Описание команд бота
   - Структура проекта
2. Финальный git commit

### Ожидаемый результат:
- README позволяет новому разработчику запустить проект за < 10 минут
- Проект готов к демонстрации

---

## Сводная таблица этапов

| Этап | Название | Ключевые файлы |
|------|---------|----------------|
| 1 | Инициализация проекта | `requirements.txt`, `bot/config.py`, `.env.example` |
| 2 | БД — модели и миграции | `bot/models/`, `migrations/`, `bot/database.py` |
| 3 | Сервис пользователей | `bot/services/user_service.py` |
| 4 | Системный промпт Селены | `bot/prompts/selena.py` |
| 5 | Сервис OpenRouter | `bot/services/openrouter_service.py` |
| 6 | FSM States и клавиатуры | `bot/states/`, `bot/keyboards/` |
| 7 | Хендлеры команд и FSM | `bot/handlers/` |
| 8 | Точка входа и запуск | `bot/main.py` |
| 9 | Конфигурация деплоя | `railway.json`, `Procfile` |
| 10 | README и документация | `README.md` |
