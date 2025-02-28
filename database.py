import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "finance.db"

def init_db():
    """Initialize the database and create the expenses table if it does not exist."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Create expenses table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  date TEXT, 
                  amount REAL, 
                  category TEXT, 
                  note TEXT)''')
    
    conn.commit()
    conn.close()

def add_expense(date, amount, category, note):
    """Add an expense to the database while preventing duplicates."""
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    # ✅ DEBUG: Print values before inserting
    print(f"Adding Expense: {date}, {amount}, {category}, {note}")

    # Prevent duplicate entries
    c.execute('''SELECT COUNT(*) FROM expenses 
                 WHERE date=? AND amount=? AND category=? AND note=?''', 
              (date, amount, category, note))
    
    if c.fetchone()[0] == 0:
        c.execute('''INSERT INTO expenses (date, amount, category, note)
                     VALUES (?, ?, ?, ?)''', (date, amount, category, note))
        conn.commit()
        print("Expense added successfully!")  # ✅ Debugging statement
    else:
        print("Duplicate expense detected, skipping insert.")  # ✅ Debugging statement
    
    conn.close()


def get_expenses():
    """Fetch all expenses from the database and return as a Pandas DataFrame."""
    conn = sqlite3.connect("finance.db")

    query = '''SELECT date, amount, category, note FROM expenses ORDER BY date DESC'''
    df = pd.read_sql_query(query, conn)

    conn.close()

    # ✅ DEBUG: Print retrieved expenses
    print("Expenses Retrieved from DB:")
    print(df)

    return df


def delete_expense(date, amount, category, note):
    """Delete a specific expense entry from the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    c.execute('''DELETE FROM expenses 
                 WHERE date=? AND amount=? AND category=? AND note=?''', 
              (date, amount, category, note))
    
    conn.commit()
    conn.close()

def clear_expenses():
    """Deletes all expense records from the database."""
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()
    
    # ✅ Delete all data from the table
    c.execute("DELETE FROM expenses")
    
    conn.commit()
    conn.close()

