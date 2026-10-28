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


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@app.post("/api/expenses/", response_model=ExpenseRead, status_code=201)
async def add_expense_endpoint(expense: ExpenseCreate, db: AsyncSession = Depends(get_db)):
    """Добавляет новый расход."""
    return await create_expense(db, expense)


@app.get("/api/expenses/", response_model=list[ExpenseRead])
async def list_expenses_endpoint(db: AsyncSession = Depends(get_db)):
    """Возвращает список всех расходов."""
    return await get_all_expenses(db)


@app.get("/api/health")
async def health_check():
    """Эндпоинт для проверки работоспособности API."""
    return {"status": "ok"}
