import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import numpy as np
from database import init_db, add_expense, get_expenses, delete_expense
import sqlite3

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
    st.header("Expense Tracker")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Add expense form
        with st.form("expense_form"):
            amount = st.number_input("Amount", min_value=0.0)
            category = st.selectbox("Category", 
                ["Food", "Transport", "Entertainment", "Bills", "Shopping", "Other"])
            date = st.date_input("Date")
            note = st.text_input("Note")
            submitted = st.form_submit_button("Add Expense")
            
            if submitted:
                add_expense(date.strftime("%Y-%m-%d"), amount, category, note)
                st.success("Expense added successfully!")
                st.rerun()
    
    with col2:
        # Display expenses
        expenses = get_expenses()
        if not expenses.empty:
            st.subheader("Recent Expenses")
            
            # Create a dataframe with a delete button column
            for idx, row in expenses.iterrows():
                cols = st.columns([2, 2, 2, 3, 1])
                cols[0].write(row['date'])
                cols[1].write(f"${row['amount']:.2f}")
                cols[2].write(row['category'])
                cols[3].write(row['note'])
                if cols[4].button('🗑️', key=f"del_{idx}_{row['date']}_{row['amount']}"):
                    delete_expense(row['date'], row['amount'], row['category'], row['note'])
                    st.success("Expense deleted!")
                    st.rerun()
            
            # Create pie chart of expenses by category
            fig = px.pie(expenses, values='amount', names='category', 
                        title='Expenses by Category')
            st.plotly_chart(fig)

def show_investment_portfolio():
    st.header("Investment Portfolio")
    
    # Sample stock portfolio
    stocks = ['AAPL', 'GOOGL', 'MSFT']
    
    # Fetch real-time stock data
    cols = st.columns(len(stocks))
    for idx, stock in enumerate(stocks):
        with cols[idx]:
            try:
                # Download data with progress=False to avoid unnecessary output
                data = yf.download(stock, 
                                 start="2023-01-01", 
                                 end=datetime.now(), 
                                 progress=False)
                
                if len(data) > 0:  # Check if we have data
                    # Create figure using graph_objects
                    fig = go.Figure()
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data['Close'].values,  # Explicitly get values
                            mode='lines',
                            name=stock
                        )
                    )
                    fig.update_layout(
                        title=f'{stock} Stock Price',
                        xaxis_title="Date",
                        yaxis_title="Price (USD)",
                        height=400,
                        width=None  # Let Streamlit handle the width
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No data available for {stock}")
            except Exception as e:
                st.error(f"Error fetching data for {stock}: {str(e)}")

def show_budget_planning():
    st.header("Budget Planning")
    
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
        fig = go.Figure(data=[go.Pie(labels=['Needs', 'Wants', 'Savings'],
                                    values=[needs, wants, savings])])
        fig.update_layout(title="Budget Breakdown")
        st.plotly_chart(fig)
        
        # Display monetary values
        st.subheader("Monthly Breakdown")
        st.write(f"Needs: ${income * needs/100:.2f}")
        st.write(f"Wants: ${income * wants/100:.2f}")
        st.write(f"Savings: ${income * savings/100:.2f}")

if __name__ == "__main__":
    main()