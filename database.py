import sqlite3
import pandas as pd
from datetime import datetime

def init_db():
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    # Create expenses table
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (date TEXT, amount REAL, category TEXT, note TEXT)''')
    
    conn.commit()
    conn.close()

def add_expense(date, amount, category, note):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    c.execute('''INSERT INTO expenses (date, amount, category, note)
                 VALUES (?, ?, ?, ?)''', (date, amount, category, note))
    
    conn.commit()
    conn.close()

def get_expenses():
    conn = sqlite3.connect('finance.db')
    
    query = '''SELECT * FROM expenses ORDER BY date DESC'''
    df = pd.read_sql_query(query, conn)
    
    conn.close()
    
    return df 

def delete_expense(date, amount, category, note):
    conn = sqlite3.connect('finance.db')
    c = conn.cursor()
    
    c.execute('''DELETE FROM expenses 
                 WHERE date=? AND amount=? AND category=? AND note=?''', 
              (date, amount, category, note))
    
    conn.commit()
    conn.close() 