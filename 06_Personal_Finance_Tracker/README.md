# Personal Finance Tracker

## Business Problem
Individuals often lose track of their income and expenses across multiple 
categories, making it hard to understand spending habits and manage 
money wisely.

## Approach
- Designed a SQLite database (via SQLAlchemy ORM) to store income and expense records
- Built a Streamlit app for users to log transactions and categorize them
- Visualized spending patterns and category-wise breakdowns using Plotly

## Tools & Libraries
Python, Streamlit, SQLite, SQLAlchemy, Plotly

## Key Insight
Persisting data with SQLAlchemy/SQLite (instead of resetting on every 
app run) makes the tracker genuinely usable over time, mirroring how a 
real personal finance app would need to behave.

## Files
- Streamlit app script
- SQLite database file