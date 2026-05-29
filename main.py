from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import os
from dotenv import load_dotenv

# ─── Load Environment Variables ───────────────────────────────────────────────
load_dotenv()

# ─── FastAPI App ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Expense Tracker API",
    description="REST API for Expense Tracker Management System",
    version="1.0.0"
)

# ─── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Pydantic Model ────────────────────────────────────────────────────────────
class ExpenseModel(BaseModel):
    title: str
    payment_method: str
    amount: float
    category: str
    spent_at: str

# ─── Database Connection ───────────────────────────────────────────────────────
def get_connection():
    return mysql.connector.connect(
        host=os.getenv("db_host"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password"),
        database=os.getenv("db_database"),
        port=int(os.getenv("db_port", 3306))
    )

# ─── Init Table ────────────────────────────────────────────────────────────────
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses1 (
            expense_id     INT AUTO_INCREMENT PRIMARY KEY,
            title          VARCHAR(200)  NOT NULL,
            payment_method VARCHAR(50)   NOT NULL,
            amount         FLOAT         NOT NULL,
            category       VARCHAR(100)  NOT NULL,
            spent_at       DATE          NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()

# ─── Health Check ──────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "Expense Tracker API is running successfully ✅"}

# ─── Add Expense ───────────────────────────────────────────────────────────────
@app.post("/expenses")
def add_expenses(expense: ExpenseModel):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO expenses1 (title, payment_method, amount, category, spent_at)
               VALUES (%s, %s, %s, %s, %s)""",
            (expense.title, expense.payment_method, expense.amount,
             expense.category, expense.spent_at)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Expense Added Successfully ✅"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Get All Expenses ──────────────────────────────────────────────────────────
@app.get("/get_expenses")
def get_expenses():
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM expenses1 ORDER BY spent_at DESC")
        data   = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"expenses": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Get Single Expense ────────────────────────────────────────────────────────
@app.get("/get_expenses_single/{expenses_id}")
def get_single_expense(expenses_id: int):
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM expenses1 WHERE expense_id = %s", (expenses_id,))
        data   = cursor.fetchone()
        cursor.close()
        conn.close()
        if not data:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"expenses_data": data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Update Expense ────────────────────────────────────────────────────────────
@app.put("/update_expenses/{expenses_id}")
def update_expenses(expenses_id: int, expense: ExpenseModel):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE expenses1
               SET title=%s, payment_method=%s, amount=%s, category=%s, spent_at=%s
               WHERE expense_id=%s""",
            (expense.title, expense.payment_method, expense.amount,
             expense.category, expense.spent_at, expenses_id)
        )
        conn.commit()
        rows = cursor.rowcount
        cursor.close()
        conn.close()
        if rows == 0:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"message": "Expense Updated Successfully ✅"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Delete Expense ────────────────────────────────────────────────────────────
@app.delete("/delete_expense/{expense_id}")
def delete_expense(expense_id: int):
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses1 WHERE expense_id = %s", (expense_id,))
        conn.commit()
        rows = cursor.rowcount
        cursor.close()
        conn.close()
        if rows == 0:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"message": "Expense Deleted Successfully ✅"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Search Expenses ───────────────────────────────────────────────────────────
@app.get("/search_expenses")
def search_expenses(search_text: str):
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM expenses1 WHERE title LIKE %s OR category LIKE %s",
            (f"%{search_text}%", f"%{search_text}%")
        )
        data   = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"expenses": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Sort Expenses ─────────────────────────────────────────────────────────────
@app.get("/sort_expenses")
def sort_expenses(sort_by: str, order_by: str):
    allowed_columns = ["payment_method", "amount", "category", "spent_at", "title"]
    allowed_orders  = ["asc", "desc"]
    if sort_by not in allowed_columns or order_by not in allowed_orders:
        raise HTTPException(status_code=400, detail="Invalid sort parameters")
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM expenses1 ORDER BY {sort_by} {order_by}")
        data   = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"expenses": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Filter Expenses ───────────────────────────────────────────────────────────
@app.get("/filter_expenses/{filter_by}")
def filter_expenses(filter_by: str):
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM expenses1 WHERE category = %s", (filter_by,))
        data   = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"expenses": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ─── Analyze Expenses ──────────────────────────────────────────────────────────
@app.get("/analyze_expenses/{analyze_by}")
def analyze_expenses(analyze_by: str):
    allowed = ["category", "payment_method", "spent_at"]
    if analyze_by not in allowed:
        raise HTTPException(status_code=400, detail="Invalid analyze field")
    try:
        conn   = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {analyze_by}, SUM(amount) AS total, COUNT(*) AS count "
            f"FROM expenses1 GROUP BY {analyze_by} ORDER BY total DESC"
        )
        data   = cursor.fetchall()
        cursor.close()
        conn.close()
        return {"expenses": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
