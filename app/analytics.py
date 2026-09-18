import pandas as pd
import plotly.express as px
from datetime import datetime

def get_analytics_data(expenses):
    """Аналитика с использованием Pandas"""
    if not expenses:
        return {"message": "Нет данных"}

    data = [{
        "id": e.id,
        "amount": e.amount,
        "category": e.category,
        "description": e.description,
        "created_at": e.created_at
    } for e in expenses]

    df = pd.DataFrame(data)
    df["created_at"] = pd.to_datetime(df["created_at"])

    total = df["amount"].sum()
    average = df["amount"].mean()
    max_expense = df.loc[df["amount"].idxmax()]

    by_category = df.groupby("category")["amount"].agg(["sum", "count", "mean"])
    by_category = by_category.sort_values("sum", ascending=False)

    df["month"] = df["created_at"].dt.to_period("M").astype(str)
    by_month = df.groupby("month")["amount"].sum()

    return {
        "total": total,
        "average": average,
        "max_expense": {
            "amount": max_expense["amount"],
            "category": max_expense["category"],
            "date": max_expense["created_at"].strftime("%Y-%m-%d")
        },
        "by_category": by_category.to_dict(),
        "by_month": by_month.to_dict(),
        "total_records": len(df)
    }


def create_category_chart(expenses):
    """Возвращает данные для графика в формате JSON"""
    if not expenses:
        return {"message": "Нет данных"}

    data = [{
        "category": e.category,
        "amount": e.amount
    } for e in expenses]

    df = pd.DataFrame(data)
    category_totals = df.groupby("category")["amount"].sum().reset_index()

    return {
        "categories": category_totals["category"].tolist(),
        "amounts": category_totals["amount"].tolist(),
        "colors": px.colors.qualitative.Vivid[:len(category_totals)]
    }
