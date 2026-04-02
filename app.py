from flask import Flask, render_template, request, redirect, url_for, abort
import sqlite3

app = Flask(__name__)

DATABASE = "expenses.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            cost_gbp REAL NOT NULL,
            description TEXT NOT NULL,
            expense_type TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db_connection()
    expenses = conn.execute("SELECT * FROM expenses ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", expenses=expenses)

@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if request.method == "POST":
        date = request.form["date"].strip()
        cost_gbp = request.form["cost_gbp"].strip()
        description = request.form["description"].strip()
        expense_type = request.form["expense_type"].strip()

        if not date or not cost_gbp or not description or not expense_type:
            return "All fields are required.", 400

        try:
            cost_gbp = float(cost_gbp)
            if cost_gbp < 0:
                return "Cost must be a positive value.", 400
        except ValueError:
            return "Invalid cost entered.", 400

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO expenses (date, cost_gbp, description, expense_type) VALUES (?, ?, ?, ?)",
            (date, cost_gbp, description, expense_type)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("view_expenses"))

    return render_template("add_expense.html")

@app.route("/expenses")
def view_expenses():
    conn = get_db_connection()
    expenses = conn.execute("SELECT * FROM expenses ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("expenses.html", expenses=expenses)

@app.route("/expenses/<int:expense_id>")
def expense_detail(expense_id):
    conn = get_db_connection()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?",
        (expense_id,)
    ).fetchone()
    conn.close()

    if expense is None:
        abort(404)

    return render_template("expense_detail.html", expense=expense)

@app.route("/delete/<int:id>", methods=["POST"])
def delete_expense(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for("view_expenses"))

if __name__ == "__main__":
    init_db()
    app.run(debug=True)