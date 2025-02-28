import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import yfinance as yf
from datetime import datetime
from database import init_db, add_expense, get_expenses, delete_expense, clear_expenses

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

def show_investment_portfolio():
    st.header("📈 Investment Portfolio")
    
    # Sample stock portfolio
    stocks = ['AAPL', 'GOOGL', 'MSFT']
    
    # Fetch real-time stock data
    cols = st.columns(len(stocks))
    
    for idx, stock in enumerate(stocks):
        with cols[idx]:
            try:
                st.write(f"Fetching data for {stock}...")  # ✅ Debugging message
                ticker = yf.Ticker(stock)
                
                data = ticker.history(period="1mo", interval="1d")

                # ✅ DEBUG: Print the actual returned data
                st.write(f"📊 Raw Data for {stock}:")
                st.write(data)

                if "Close" in data.columns and not data["Close"].dropna().empty:
                    st.write(f"✅ Data Found for {stock}: {data.shape}")  # ✅ Debugging output

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode='lines', name=stock))
                    fig.update_layout(title=f'{stock} Last Month', height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"⚠ No valid closing price data found for {stock}.")
                    st.write("✅ Debug Info: Available columns:", data.columns.tolist())  # ✅ Debugging

            except Exception as e:
                st.error(f"❌ Error fetching data for {stock}: {str(e)}")
                st.write("Error Type:", type(e).__name__)  # ✅ Show error type




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
