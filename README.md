# Сервис записи на приём к специалисту

Учебный веб-сервис для варианта 3 по дисциплине «Оптимизация клиент-серверных приложений».

## Назначение

Сервис хранит расписание специалистов слотами, показывает свободные слоты по выбранной услуге и позволяет пользователю забронировать слот. Слот нельзя забронировать повторно, а отменённая запись возвращает слот в свободные.

## Требования

- Python 3.14
- PostgreSQL 18
- pip
- браузер

## Установка и запуск

```text
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python scripts/init_db.py
python scripts/seed_small.py
uvicorn app.main:app --reload --port 8000
```

Интерфейс: http://localhost:8000

Учётная запись: demo / demo

## Рабочее наполнение

```text
python scripts/seed_working.py
```

Рабочее наполнение создаёт 200000 слотов. Ориентир методички для варианта 3 — 200000 слотов и 50000–100000 записей.

## Тесты

```text
pytest -q
```

## Программный интерфейс

| Метод и путь | Параметры | Ответ | Ошибки |
|---|---|---|---|
| POST /api/auth/login | username, password | пользователь | 401 |
| POST /api/auth/logout | — | status | — |
| GET /api/specialists | — | список специалистов | 401 |
| GET /api/services | — | список услуг | 401 |
| GET /api/slots | specialist_id, service_id, available, limit | список слотов | 401 |
| GET /api/appointments | page, size, status | items, total | 401 |
| GET /api/appointments/{id} | id | запись | 401, 404 |
| POST /api/appointments | specialist_id, service_id, slot_id | созданная запись | 401, 409 |
| POST /api/appointments/{id}/cancel | id | обновлённая запись | 401, 404, 409 |
| GET /api/summary | — | сводные показатели | 401 |

## Три обязательных экрана

В минимальном клиенте предусмотрены:
1. список доступных слотов;
2. просмотр собственных записей;
3. сводка.

## Префикс

В работе используется префикс `romanov_andrey`.

## Ограничения первого задания

В первой версии не используются дополнительные индексы сверх первичных и внешних ключей, кеширование, очереди сообщений и фоновая обработка.
