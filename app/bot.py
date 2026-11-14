import asyncio
import logging
from decimal import Decimal

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.expense import Expense

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

dp = Dispatcher()
CATEGORIES = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Одежда", "Другое"]


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        f"Привет, {message.from_user.username or 'друг'}! \n\n"
        "Я бот для учета расходов.\n\n"
        "Команды:\n"
        "/add - Добавить расход (формат: сумма категория описание)\n"
        "/stats - Показать статистику\n"
        "/categories - Список категорий\n"
        "/help - Помощь"
    )


@dp.message(Command("add"))
async def cmd_add(message: Message) -> None:
    await message.answer(
        "Введите расход в формате:\n"
        "`сумма категория описание`\n\n"
        "Пример: `500 Еда Обед в кафе`\n\n"
        f"Доступные категории: {', '.join(CATEGORIES)}",
        parse_mode="Markdown",
    )


@dp.message(F.text & ~F.text.startswith("/"))
async def process_expense(message: Message) -> None:
    parts = message.text.split(maxsplit=2)

    if len(parts) < 2:
        await message.answer(
            "Неверный формат. Используйте: `сумма категория описание`",
            parse_mode="Markdown",
        )
        return

    try:
        amount = Decimal(parts[0].replace(",", "."))
    except Exception:
        await message.answer("Сумма должна быть числом (например, 500 или 500.50)")
        return

    category = parts[1].capitalize()
    if category not in CATEGORIES:
        await message.answer(f"Неверная категория. Доступные: {', '.join(CATEGORIES)}")
        return

    description = parts[2] if len(parts) > 2 else "Без описания"
    title = f"{category}: {description}"

    async with AsyncSessionLocal() as db:
        try:
            new_expense = Expense(
                telegram_id=message.from_user.id,
                title=title,
                amount=amount,
                category=category,
            )
            db.add(new_expense)
            await db.commit()
            await message.answer(
                f"Расход добавлен!\n\nСумма: {amount} руб.\n"
                f"Категория: {category}\nОписание: {description}"
            )
        except Exception as e:
            logger.error(f"Ошибка при сохранении расхода: {e}")
            await db.rollback()
            await message.answer("Произошла ошибка при сохранении расхода. Попробуйте позже.")


@dp.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Expense).where(Expense.telegram_id == message.from_user.id)
        )
        expenses = result.scalars().all()

        if not expenses:
            await message.answer("У вас пока нет расходов. Добавьте первый через /add")
            return

        total = sum(e.amount for e in expenses)
        by_category: dict[str, Decimal] = {}
        for e in expenses:
            by_category[e.category] = by_category.get(e.category, Decimal("0")) + e.amount

        stats_text = "Ваша статистика:\n\n"
        stats_text += f"Всего расходов: {len(expenses)}\n"
        stats_text += f"Общая сумма: {total:.2f} руб.\n\nПо категориям:\n"
        for cat, amount in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            stats_text += f"• {cat}: {amount:.2f} руб.\n"

        await message.answer(stats_text)


@dp.message(Command("categories"))
async def cmd_categories(message: Message) -> None:
    await message.answer("Доступные категории:\n\n" + "\n".join(f"• {cat}" for cat in CATEGORIES))


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    help_text = (
        "/start - Начать работу\n"
        "/add - Добавить расход\n"
        "/stats - Статистика\n"
        "/categories - Список категорий\n"
        "/help - Справка"
    )
    await message.answer(help_text)


async def main() -> None:
    token = settings.active_bot_token
    bot = Bot(token=token)
    logger.info("Бот успешно подключен к Telegram!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
