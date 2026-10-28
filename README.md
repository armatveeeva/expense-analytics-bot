# Аналитика расходов — приложение для управления личными финансами

[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Aiogram](https://img.shields.io/badge/Aiogram-3.x-blue)](https://docs.aiogram.dev/)
[![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat&logo=plotly&logoColor=white)](https://plotly.com/)

Асинхронный Telegram-бот и веб-дашборд для учета и аналитики расходов.  
Проект построен на принципах чистой архитектуры с разделением на слои (Routers → Services → Repositories).

## Архитектура

```mermaid
flowchart LR
    U[Пользователь] -->|/add 500 еда| B[Telegram Bot · aiogram]
    W[Браузер] --> A[FastAPI · Routers]
    B --> S[Services]
    A --> S
    S --> R[Repositories]
    R --> DB[(PostgreSQL / SQLite)]
    S -->|pandas| AN[Аналитика] --> A
    A -->|Plotly JSON| W
   ```

## Технологический стек

- **Язык программирования:** Python 3.11+
- **Telegram Bot Framework:** Aiogram 3.x (асинхронный фреймворк)
- **Web Backend:** Flask (REST API)
- **ORM:** SQLAlchemy (архитектура, готовая к переходу на PostgreSQL)
- **База данных:** SQLite (локальная разработка), PostgreSQL (продакшен)
- **Анализ данных:** Pandas (агрегация, группировка, временные ряды)
- **Визуализация:** Plotly (интерактивные графики)
- **Frontend:** HTML5, CSS3 (адаптивный дизайн, Grid/Flexbox)
- **Тестирование:** Pytest
- **Управление конфигурацией:** python-dotenv

## Быстрый старт

### Предварительные требования

- Python 3.11 или выше
- Действующий токен Telegram-бота (получается через @BotFather)

### Установка и настройка

1. Клонирование и переход в директорию
git clone https://github.com/armatveeeva/expense-analytics-bot.git
cd expense-analytics-bot

2. Установка зависимостей
poetry install

3. Настройка окружения
cp .env.example .env
# Отредактируйте .env, добавив BOT_TOKEN и DATABASE_URL

4. Применение миграций БД
poetry run alembic upgrade head

5. Запуск API (дашборд доступен по адресу http://localhost:8000/docs)
poetry run uvicorn app.api.main:app --reload --port 8000
