from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100, description="Название расхода")
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2, description="Сумма расхода")
    category: str = Field(min_length=1, max_length=50, description="Категория")


class ExpenseRead(BaseModel):
    id: int
    title: str
    amount: Decimal
    category: str

    model_config = {"from_attributes": True}
