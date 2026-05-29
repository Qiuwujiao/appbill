import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bills
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  create_time TEXT,
                  amount REAL,
                  type TEXT,
                  category TEXT,
                  shop TEXT,
                  remark TEXT)''')
    conn.commit()
    conn.close()

def reset_db_id():
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    c.execute('DELETE FROM bills')
    c.execute('DELETE FROM sqlite_sequence WHERE name="bills"')
    conn.commit()
    conn.close()

def add_bill(bill):
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    amount = round(bill['amount'], 2)
    c.execute('INSERT INTO bills (create_time, amount, type, category, shop, remark) VALUES (?,?,?,?,?,?)',
              (bill['time'], amount, bill['type'], bill['category'], bill['shop'], bill['remark']))
    conn.commit()
    conn.close()

def query_all_bill():
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    c.execute('SELECT * FROM bills ORDER BY create_time DESC')
    res = c.fetchall()
    conn.close()
    return res

def delete_bill(bid):
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    c.execute('DELETE FROM bills WHERE id=?', (bid,))
    conn.commit()
    conn.close()

def delete_all_bills():
    reset_db_id()

def update_bill_category(bid, cat):
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    c.execute('UPDATE bills SET category=? WHERE id=?', (cat, bid))
    conn.commit()
    conn.close()

def update_bill_all(bid, create_time, amount, category, shop):
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    amount = round(amount, 2)
    c.execute('UPDATE bills SET create_time=?, amount=?, category=?, shop=? WHERE id=?',
              (create_time, amount, category, shop, bid))
    conn.commit()
    conn.close()

def get_bills_by_category(cat):
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    c.execute('SELECT id, shop, create_time, ABS(amount) FROM bills WHERE category=?', (cat,))
    res = c.fetchall()
    conn.close()
    return res

def get_expense_by_category():
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    c.execute('SELECT category, ROUND(SUM(ABS(amount)), 2) FROM bills WHERE type="支出" GROUP BY category HAVING SUM(ABS(amount))>0')
    res = c.fetchall()
    conn.close()
    return res

def get_analysis_by_period(period, start=None, end=None):
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    if period == "custom":
        c.execute('SELECT SUM(ABS(amount)), COUNT(*) FROM bills WHERE type="支出" AND create_time BETWEEN ? AND ?', (start, end))
    total, count = c.fetchone()
    total = round(total or 0, 2)
    count = count or 0
    days = 1
    if start and end:
        d1 = datetime.strptime(start, "%Y.%m.%d")
        d2 = datetime.strptime(end, "%Y.%m.%d")
        days = (d2 - d1).days + 1
    avg = round(total / days, 2) if days > 0 else 0
    conn.close()
    return {"total": total, "count": count, "avg": avg}

def get_category_ratio_by_period(period, start=None, end=None):
    conn = sqlite3.connect('bill.db')
    c = conn.cursor()
    if period == "custom":
        c.execute('SELECT category, ROUND(SUM(ABS(amount)), 2) FROM bills WHERE type="支出" AND create_time BETWEEN ? AND ? GROUP BY category', (start, end))
    data = c.fetchall()
    conn.close()
    total = sum([x[1] for x in data]) if data else 0
    if total == 0:
        return []
    res = []
    for cat, amt in data:
        pct = round(amt / total * 100, 1)
        res.append((cat, pct))
    return res