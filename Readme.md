# Expense Tracker — Backend

REST API for the Expense Tracker Management System, built with **FastAPI** and **MySQL**.

---

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Programming Language |
| FastAPI | REST API Framework |
| MySQL | Database |
| Pydantic | Data Validation |
| Uvicorn | ASGI Server |
| python-dotenv | Environment Variables |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Health Check |
| POST | /expenses | Add Expense |
| GET | /get_expenses | Get All Expenses |
| GET | /get_expenses_single/{id} | Get Single Expense |
| PUT | /update_expenses/{id} | Update Expense |
| DELETE | /delete_expense/{id} | Delete Expense |
| GET | /search_expenses | Search Expenses |
| GET | /sort_expenses | Sort Expenses |
| GET | /filter_expenses/{filter_by} | Filter by Category |
| GET | /analyze_expenses/{analyze_by} | Analyze Expenses |

---

## Database Setup

```sql
CREATE DATABASE expenses_db;

CREATE TABLE expenses1 (
    expense_id     INT AUTO_INCREMENT PRIMARY KEY,
    title          VARCHAR(200) NOT NULL,
    payment_method VARCHAR(50)  NOT NULL,
    amount         FLOAT        NOT NULL,
    category       VARCHAR(100) NOT NULL,
    spent_at       DATE         NOT NULL
);
```

---

## Environment Variables

Create a `.env` file:

```env
db_host=localhost
db_user=root
db_password=your_password
db_database=expenses_db
db_port=3306
```

---

## Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at: `http://127.0.0.1:8000`

API Docs at: `http://127.0.0.1:8000/docs`

---

## Author

Your Name — Built for learning Full Stack Python Development.
