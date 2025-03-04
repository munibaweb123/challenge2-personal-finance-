import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import yfinance as yf
from datetime import datetime
from database import init_db, add_expense, get_expenses, delete_expense, clear_expenses
import requests

# Initialize the database
init_db()

def main():
    st.set_page_config(page_title="Finance Dashboard", layout="wide")
    st.title("💰 Personal Finance Analytics Dashboard")
    
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Expense Tracker", "Investment Portfolio", "Budget Planning"])
    
    if page == "Expense Tracker":
        show_expense_tracker()
    elif page == "Investment Portfolio":
        show_investment_portfolio()
    else:
        show_budget_planning()

def show_expense_tracker():
    st.header("📊 Expense Tracker")

    col1, col2 = st.columns(2)

    with col1:
        # 🔴 Button to Clear All Expenses
        if st.button("❌ Clear All Expenses"):
            clear_expenses()  # Calls function from database.py
            st.success("All expenses deleted successfully!")
            st.rerun()

        # 📂 File Upload Section
        uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])
        
        if uploaded_file is not None:
            try:
                # Read CSV or Excel file
                if uploaded_file.name.endswith(".csv"):
                    df = pd.read_csv(uploaded_file, encoding="utf-8", sep=",")
                else:
                    df = pd.read_excel(uploaded_file)

                # 🔹 Normalize column names (remove spaces & convert to lowercase)
                df.columns = df.columns.str.strip().str.lower()

                # 🔹 Convert "date" column to string format
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

                # ✅ Remove duplicates before inserting into the database
                df = df.drop_duplicates()

                # 🔍 Show preview of uploaded data
                st.subheader("Uploaded Data Preview")
                st.dataframe(df)

                # 🔹 Insert expenses into the database
                for _, row in df.iterrows():
                    add_expense(row["date"], row["amount"], row["category"], row["note"])

                st.success("Expenses uploaded successfully!")
                st.rerun()

            except Exception as e:
                st.error(f"Error processing file: {e}")

        # 🔹 Manual Expense Entry
        with st.form("expense_form"):
            amount = st.number_input("Amount", min_value=0.0)
            category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"])
            date = st.date_input("Date")
            note = st.text_input("Note")
            submitted = st.form_submit_button("Add Expense")

            if submitted:
                add_expense(date.strftime("%Y-%m-%d"), amount, category, note)
                st.success("Expense added successfully!")
                st.rerun()

    with col2:
        # 🔍 Display Existing Expenses
        expenses = get_expenses()
        
        if expenses.empty:
            st.info("No expenses found. Add new expenses or upload a file.")
        else:
            st.subheader("Recent Expenses")
            st.dataframe(expenses)  # Display as DataFrame

            # 📊 Pie Chart for Category-wise Expenses
            fig = px.pie(expenses, values='amount', names='category', title='Expenses by Category')
            st.plotly_chart(fig)

import requests

def fetch_stock_price(symbol):
    """Fetch stock data from Alpha Vantage"""
    api_key = "RVO6XQ3L05Z09UN8"  # 🔹 Replace with your API key
    url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
    response = requests.get(url)
    data = response.json()

    if "Time Series (Daily)" in data:
        df = pd.DataFrame(data["Time Series (Daily)"]).T
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df.rename(columns={"4. close": "Close"})  # 🔹 Standardize column name
        return df
    else:
        return None

def show_investment_portfolio():
    st.header("📈 Investment Portfolio")
    
    stocks = ['AAPL', 'GOOGL', 'MSFT']
    
    cols = st.columns(len(stocks))
    
    for idx, stock in enumerate(stocks):
        with cols[idx]:
            st.write(f"Fetching data for {stock}...")
            data = fetch_stock_price(stock)

            if data is not None and "Close" in data.columns:
                st.write(f"✅ Data Found for {stock}: {data.shape}")
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode='lines', name=stock))
                fig.update_layout(title=f'{stock} Last Month', height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"⚠ No valid closing price data found for {stock}.")



def show_budget_planning():
    st.header("📊 Budget Planning")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly income input
        income = st.number_input("Monthly Income", min_value=0.0, value=5000.0)
        
        # Budget allocation sliders
        st.subheader("Budget Allocation")
        needs = st.slider("Needs (50-60%)", 0, 100, 50)
        wants = st.slider("Wants (20-30%)", 0, 100, 30)
        savings = st.slider("Savings (20-30%)", 0, 100, 20)
    
    with col2:
        # Display budget breakdown
        fig = go.Figure(data=[go.Pie(labels=['Needs', 'Wants', 'Savings'], values=[needs, wants, savings])])
        fig.update_layout(title="Budget Breakdown")
        st.plotly_chart(fig)
        
        # Display monetary values
        st.subheader("Monthly Breakdown")
        st.write(f"Needs: ${income * needs/100:.2f}")
        st.write(f"Wants: ${income * wants/100:.2f}")
        st.write(f"Savings: ${income * savings/100:.2f}")

if __name__ == "__main__":
    main()
