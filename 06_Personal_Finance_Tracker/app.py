import streamlit as st
import pandas as pd
from crud import add_transaction, get_all_transactions, update_transaction, delete_transaction
import plotly.express as px

st.set_page_config(page_title="Finance Tracker", page_icon="💰", layout="wide")
st.title("💰 Personal Finance Tracker")

# ---------- SUMMARY METRICS ----------
transactions = get_all_transactions()
if transactions:
    total_income  = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    balance       = total_income - total_expense

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income",  f"₹{total_income:,.0f}")
    col2.metric("Total Expense", f"₹{total_expense:,.0f}")
    col3.metric("Balance",       f"₹{balance:,.0f}", delta=f"₹{balance:,.0f}")

# ---------- SIDEBAR — Add Transaction ----------
st.sidebar.header("Add New Transaction")

type_ = st.sidebar.selectbox("Type", ["expense", "income"])

categories_expense = ["Food", "Rent", "Transport", "Entertainment", "Health", "Shopping", "Other"]
categories_income  = ["Salary", "Freelance", "Investment", "Gift", "Other"]

if type_ == "expense":
    category = st.sidebar.selectbox("Category", categories_expense)
else:
    category = st.sidebar.selectbox("Category", categories_income)

amount      = st.sidebar.number_input("Amount (₹)", min_value=0.0, step=10.0)
description = st.sidebar.text_input("Description (optional)")

if st.sidebar.button("Add Transaction"):
    if amount == 0:
        st.sidebar.warning("Please enter an amount greater than 0.")
    else:
        add_transaction(amount, category, type_, description)
        st.sidebar.success("Transaction added!")
        st.rerun()

# ---------- MAIN AREA — View Transactions ----------
st.subheader("All Transactions")

transactions = get_all_transactions()
if not transactions:
    st.info("No transactions yet. Add one from the sidebar!")
else:
    # Convert list of SQLAlchemy objects to a pandas DataFrame
    data = []
    for t in transactions:
        data.append({
            "ID":          t.id,
            "Date":        t.date,
            "Type":        t.type,
            "Category":    t.category,
            "Amount (₹)":  t.amount,
            "Description": t.description
        })  
    
    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ---------- DELETE ----------
    st.subheader("Delete a Transaction")

    delete_id = st.number_input("Enter ID to delete", min_value=1, step=1)

    if st.button("Delete Transaction"):
        existing_ids = [t.id for t in transactions]
        if delete_id in existing_ids:
            delete_transaction(int(delete_id))
            st.success(f"Transaction {delete_id} deleted!")
            st.rerun()
        else:
            st.error(f"No transaction found with ID {delete_id}")

    # ---------- EDIT ----------
    st.subheader("Edit a Transaction")

    edit_id = st.number_input("Enter ID to edit", min_value=1, step=1, key="edit_id")

    # Find the transaction with that ID
    selected = next((t for t in transactions if t.id == edit_id), None)
    
    if selected:
        st.write(f"Editing: **{selected.category}** — ₹{selected.amount} ({selected.type})")

        new_amount      = st.number_input("New Amount (₹)", value=float(selected.amount), min_value=0.0, step=10.0)
        new_category    = st.text_input("New Category", value=selected.category)
        new_description = st.text_input("New Description", value=selected.description)

        if st.button("Update Transaction"):
            update_transaction(int(edit_id), new_amount, new_category, new_description)
            st.success("Transaction updated!")
            st.rerun()
    else:
        st.info("Enter a valid ID above to edit that transaction.")

    # ---------- CHARTS ----------
    st.subheader("📊 Spending Insights")

    df_expense = df[df["Type"] == "expense"]
    df_income  = df[df["Type"] == "income"]

    col_left, col_right = st.columns(2)

    # Pie chart — expense breakdown by category
    with col_left:
        if not df_expense.empty:
            fig_pie = px.pie(
                df_expense,
                names="Category",
                values="Amount (₹)",
                title="Expenses by Category",
                hole=0.4
            )
            fig_pie.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expense data yet.")

    # Bar chart — income vs expense total
    with col_right:
        summary_df = pd.DataFrame({
            "Type":      ["Income", "Expense"],
            "Amount (₹)": [total_income, total_expense]
        })
        fig_bar = px.bar(
            summary_df,
            x="Type",
            y="Amount (₹)",
            title="Income vs Expense",
            color="Type",
            color_discrete_map={"Income": "#2ecc71", "Expense": "#e74c3c"}
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

    # Line chart — spending over time
    st.subheader("📈 Spending Over Time")

    df["Date"] = pd.to_datetime(df["Date"])
    df_by_date = df.groupby(["Date", "Type"])["Amount (₹)"].sum().reset_index()

    fig_line = px.line(
        df_by_date,
        x="Date",
        y="Amount (₹)",
        color="Type",
        title="Daily Income & Expense Trend",
        markers=True,
        color_discrete_map={"income": "#2ecc71", "expense": "#e74c3c"}
    )
    st.plotly_chart(fig_line, use_container_width=True)