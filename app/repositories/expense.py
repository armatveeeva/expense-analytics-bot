from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate


async def create_expense(db: AsyncSession, expense_data: ExpenseCreate) -> Expense:
    """Создает новую запись о расходе в БД."""
    db_expense = Expense(**expense_data.model_dump())
    db.add(db_expense)
    await db.commit()
    await db.refresh(db_expense)
    return db_expense


async def get_all_expenses(db: AsyncSession) -> list[Expense]:
    """Возвращает все записи о расходах."""
    result = await db.execute(select(Expense))
    return list(result.scalars().all())
