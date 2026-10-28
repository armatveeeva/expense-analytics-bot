import os

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from sqlalchemy import func

from .analytics import create_category_chart, get_analytics_data
from .database import Base, SessionLocal, engine
from .models import Expense, User

load_dotenv()

Base.metadata.create_all(bind=engine)

basedir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.dirname(basedir)

app = Flask(
    __name__,
    template_folder=os.path.join(project_root, "templates"),
    static_folder=os.path.join(project_root, "static"),
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
            total_amount=total_amount,
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
    app.run(debug=os.getenv("FLASK_DEBUG") == "1", port=5000)
