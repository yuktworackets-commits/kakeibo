import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

dbPath = Path(__file__).parent / "kakeibo.db"
jpt = timezone(timedelta(hours=9))  # 日本時間（UTC+9）

colors = {
    "赤": {"emoji": "🔴", "code": "#E74C3C"},
    "オレンジ": {"emoji": "🟠", "code": "#F39C12"},
    "黄": {"emoji": "🟡", "code": "#F1C40F"},
    "緑": {"emoji": "🟢", "code": "#27AE60"},
    "青": {"emoji": "🔵", "code": "#3498DB"},
    "紫": {"emoji": "🟣", "code": "#9B59B6"},
    "茶": {"emoji": "🟤", "code": "#8D6E63"},
    "黒": {"emoji": "⚫", "code": "#34495E"},
    "白": {"emoji": "⚪", "code": "#BDC3C7"},
}
defaultColor = "緑"


def init_db():
    conn = sqlite3.connect(dbPath)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY,
            amount INTEGER NOT NULL,
            color TEXT NOT NULL,
            memo TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()
#DEFAULT ''で自動で空文字に

def add_expense(amount, color):
    now = datetime.now(jpt).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(dbPath)
    conn.execute(
        "INSERT INTO expenses (amount, color, created_at) VALUES (?, ?, ?)",
        (amount, color, now),
    )
    conn.commit()
    conn.close()


def get_expenses(year, month):
    conn = sqlite3.connect(dbPath)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM expenses WHERE created_at LIKE ? ORDER BY created_at DESC, id DESC",
        (f"{year}-{month:02d}%",),
    ).fetchall()
    conn.close()

    expenses = []
    for row in rows:
        expenses.append(dict(row))
    return expenses


def update_memo(expenseId, memo):
    conn = sqlite3.connect(dbPath)
    conn.execute(
        "UPDATE expenses SET memo = ? WHERE id = ?",
        (memo, expenseId),
    )
    conn.commit()
    conn.close()


def delete_expense(expenseId):
    conn = sqlite3.connect(dbPath)
    conn.execute(
        "DELETE FROM expenses WHERE id = ?",
        (expenseId,),
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    add_expense(1500, "緑")

    now = datetime.now(jpt)
    rows = get_expenses(now.year, now.month)
    print("登録後:", rows)

    firstId = rows[0]["id"]
    update_memo(firstId, "テストのメモ")
    print("メモ更新後:", get_expenses(now.year, now.month)[0])

    delete_expense(firstId)
    print("削除後:", get_expenses(now.year, now.month))