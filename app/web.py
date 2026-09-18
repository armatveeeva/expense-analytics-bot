from flask import Flask, render_template, jsonify
from sqlalchemy import func
from .database import engine, SessionLocal, Base
from .models import User, Expense
from .analytics import get_analytics_data, create_category_chart
import os
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.dirname(basedir)

app = Flask(
    __name__,
    template_folder=os.path.join(project_root, 'templates'),
    static_folder=os.path.join(project_root, 'static')
)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")


@app.route("/")
def index():
    db = SessionLocal()
    try:
        total_users = db.query(User).count()
        total_expenses = db.query(Expense).count()

        total_amount = db.query(func.sum(Expense.amount)).scalar() or 0

        return render_template(
            "index.html",
            total_users=total_users,
            total_expenses=total_expenses,
            total_amount=total_amount
        )
    finally:
        db.close()


@app.route("/api/analytics")
def api_analytics():
    db = SessionLocal()
    try:
        expenses = db.query(Expense).all()
        data = get_analytics_data(expenses)
        return jsonify(data)
    finally:
        db.close()


@app.route("/api/chart")
def api_chart():
    db = SessionLocal()
    try:
        expenses = db.query(Expense).all()
        chart_data = create_category_chart(expenses)
        return jsonify(chart_data)
    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
