import asyncio
import os
import ssl

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from .database import Base, SessionLocal, engine
from .models import Expense, User

ssl._create_default_https_context = ssl._create_unverified_context

load_dotenv()

Base.metadata.create_all(bind=engine)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
dp = Dispatcher()

CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Одежда", "Другое"]


def get_or_create_user(telegram_id: int, username: str, db: Session) -> User:
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id, username=username)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@dp.message(Command("start"))
async def cmd_start(message: Message):
    db = SessionLocal()
    try:
        get_or_create_user(message.from_user.id, message.from_user.username, db)
        await message.answer(
            f"Привет, {message.from_user.username or 'друг'}! 👋\n\n"
            "Я бот для учета расходов.\n\n"
            "Команды:\n"
            "/add - Добавить расход\n"
            "/stats - Показать статистику\n"
            "/categories - Список категорий\n"
            "/help - Помощь"
        )
    finally:
        db.close()


@dp.message(Command("add"))
async def cmd_add(message: Message):
    await message.answer(
        "Введите расход в формате:\n"
        "`сумма категория описание`\n\n"
        "Пример: `500 Еда Обед в кафе`\n\n"
        f"Доступные категории: {', '.join(CATEGORIES)}",
        parse_mode="Markdown",
    )


@dp.message(F.text & ~F.text.startswith("/"))
async def process_expense(message: Message):
    db = SessionLocal()
    try:
        parts = message.text.split(maxsplit=2)

        if len(parts) < 2:
            await message.answer(
                "Неверный формат. Используйте: `сумма категория описание`",
                parse_mode="Markdown",
            )
            return

        try:
            amount = float(parts[0])
        except ValueError:
            await message.answer("Сумма должна быть числом")
            return

        category = parts[1]
        if category not in CATEGORIES:
            await message.answer(
                f"Неверная категория. Доступные: {', '.join(CATEGORIES)}"
            )
            return

        description = parts[2] if len(parts) > 2 else None

        user = get_or_create_user(message.from_user.id, message.from_user.username, db)

        expense = Expense(
            user_id=user.id, amount=amount, category=category, description=description
        )
        db.add(expense)
        db.commit()

        await message.answer(
            f"Расход добавлен!\n\n"
            f"Сумма: {amount} руб.\n"
            f"Категория: {category}\n"
            f"Описание: {description or 'Нет'}"
        )
    finally:
        db.close()


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()
        if not user:
            await message.answer("Сначала используйте /start")
            return

        expenses = db.query(Expense).filter(Expense.user_id == user.id).all()

        if not expenses:
            await message.answer("У вас пока нет расходов. Добавьте первый через /add")
            return

        total = sum(e.amount for e in expenses)
        by_category = {}
        for e in expenses:
            by_category[e.category] = by_category.get(e.category, 0) + e.amount

        stats_text = "📊 Ваша статистика:\n\n"
        stats_text += f"Всего расходов: {len(expenses)}\n"
        stats_text += f"Общая сумма: {total:.2f} руб.\n\n"
        stats_text += "По категориям:\n"
        for cat, amount in sorted(
            by_category.items(), key=lambda x: x[1], reverse=True
        ):
            stats_text += f"• {cat}: {amount:.2f} руб.\n"

        await message.answer(stats_text)
    finally:
        db.close()


@dp.message(Command("categories"))
async def cmd_categories(message: Message):
    categories_text = "📂 Доступные категории:\n\n"
    for cat in CATEGORIES:
        categories_text += f"• {cat}\n"
    await message.answer(categories_text)


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Бот для учета расходов\n\n"
        "Команды:\n"
        "/start - Начать работу\n"
        "/add - Добавить расход\n"
        "/stats - Показать статистику\n"
        "/categories - Список категорий\n"
        "/help - Эта справка"
    )


async def main():
    print("Бот запускается...")

    bot = Bot(token=BOT_TOKEN)

    try:
        print("Бот успешно подключен к Telegram!")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
