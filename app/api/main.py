from collections.abc import AsyncGenerator

from fastapi import Depends, FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import AsyncSessionLocal
from app.repositories.expense import create_expense, get_all_expenses
from app.schemas.expense import ExpenseCreate, ExpenseRead

app = FastAPI(
    title="Expense Analytics API",
    description="API для управления расходами и аналитики",
    version="0.1.0",
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/api/expenses/", response_model=ExpenseRead, status_code=201)
async def add_expense_endpoint(
    expense: ExpenseCreate, db: AsyncSession = Depends(get_db)
) -> ExpenseRead:
    """Добавляет новый расход."""
    db_expense = await create_expense(db, expense)
    return ExpenseRead.model_validate(db_expense)  # type: ignore


@app.get("/api/expenses/", response_model=list[ExpenseRead])
async def list_expenses_endpoint(
    db: AsyncSession = Depends(get_db),
) -> list[ExpenseRead]:
    """Возвращает список всех расходов."""
    expenses = await get_all_expenses(db)
    return [ExpenseRead.model_validate(exp) for exp in expenses]


@app.get("/api/health")
async def health_check() -> dict[str, str]:
    """Эндпоинт для проверки работоспособности API."""
    return {"status": "ok"}
