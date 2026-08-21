# Library Catalog API

REST API для управления каталогом книг. Поддерживает CRUD-операции,
поиск с фильтрацией и пагинацией, а также обогащение данных через Open Library.

## Запуск

```bash
docker compose up -d
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.library_catalog.main:app --reload
```

Приложение запустится по адресу `http://127.0.0.1:8000`.

## Миграции

Применить все миграции:

```bash
poetry run alembic upgrade head
```

Проверить текущую миграцию:

```bash
poetry run alembic current
```

## Документация API

Swagger UI доступен по адресу:

`http://127.0.0.1:8000/docs`

Основные маршруты:

- `POST /api/v1/books` — создать книгу;
- `GET /api/v1/books` — поиск, фильтрация и пагинация;
- `GET /api/v1/books/{book_id}` — получить книгу;
- `PATCH /api/v1/books/{book_id}` — обновить книгу;
- `DELETE /api/v1/books/{book_id}` — удалить книгу;
- `GET /health` — проверить доступность приложения и БД.
