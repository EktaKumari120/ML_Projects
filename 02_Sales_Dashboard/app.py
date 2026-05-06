import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide"   
)

# ── GENERATE SAMPLE DATA ──────────────────────────────────
@st.cache_data   
def load_data():
    np.random.seed(42)
    n = 500  # 500 rows of fake sales data

    regions = ["North", "South", "East", "West"]
    products = ["Laptop", "Phone", "Tablet", "Headphones", "Charger"]

    # Generate 500 random dates in the year 2024
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(days=int(x)) for x in np.random.randint(0, 365, n)]

    df = pd.DataFrame({
        "Date": dates,
        "Region": np.random.choice(regions, n),
        "Product": np.random.choice(products, n),
        "Units_Sold": np.random.randint(1, 50, n),
        "Unit_Price": np.random.choice([499, 999, 299, 149, 29], n),
    })

    df["Revenue"] = df["Units_Sold"] * df["Unit_Price"]
    df["Month"] = df["Date"].dt.strftime("%B")   
    df["Date"] = pd.to_datetime(df["Date"])

    df.to_csv("data/sales_data.csv", index = False)
    return df

df = load_data()

# ── TITLE ─────────────────────────────────────────────────
st.title("📊 Sales Performance Dashboard")
st.markdown("Explore sales data by region, product, and time.")

# ── SIDEBAR ───────────────────────────────────────────────
st.sidebar.header("🔍 Filter Data")

# Filter 1: Region 
all_regions = df["Region"].unique().tolist()
selected_regions = st.sidebar.multiselect(
    "Select Region(s):",
    options=all_regions,
    default=all_regions   # all selected by default
)

# Filter 2: Product
all_products = df["Product"].unique().tolist()
selected_products = st.sidebar.multiselect(
    "Select Product(s):",
    options=all_products,
    default=all_products
)

# Filter 3: Date Range
st.sidebar.subheader("Select Date Range")

min_date = df["Date"].min().date()   # earliest date in data
max_date = df["Date"].max().date()   # latest date in data

start_date, end_date = st.sidebar.slider(
    "Date Range:",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)   # default = full range selected
)

# ── APPLY FILTERS ─────────────────────────────────────────
filtered_df = df[
    (df["Region"].isin(selected_regions)) &
    (df["Product"].isin(selected_products)) &
    (df["Date"].dt.date >= start_date) &
    (df["Date"].dt.date <= end_date)
]

# ── KPI METRICS (top row) ──────────────────────────────────
col1, col2, col3 = st.columns(3)

col1.metric("💰 Total Revenue", f"${filtered_df['Revenue'].sum():,.0f}")
col2.metric("📦 Units Sold", f"{filtered_df['Units_Sold'].sum():,}")
col3.metric("🧾 Total Orders", f"{len(filtered_df):,}")

st.divider()

# ── CHART 1: Revenue by Region (Bar Chart) ─────────────────
st.subheader("Revenue by Region")

region_revenue = filtered_df.groupby("Region")["Revenue"].sum().reset_index()

fig1 = px.bar(
    region_revenue,
    x="Region",
    y="Revenue",
    color="Region",         # different color per bar
    text_auto=True,         # shows value on top of bar
    title="Total Revenue per Region"
)
st.plotly_chart(fig1, use_container_width=True)

# ── CHART 2: Revenue Over Time (Line Chart) ────────────────
st.subheader("Revenue Over Time")

monthly_revenue = (
    filtered_df.groupby(filtered_df["Date"].dt.to_period("M"))["Revenue"]
    .sum()
    .reset_index()
)
monthly_revenue["Date"] = monthly_revenue["Date"].astype(str)

fig2 = px.line(
    monthly_revenue,
    x="Date",
    y="Revenue",
    title="Monthly Revenue Trend",
    markers=True   # shows dot at each data point
)
st.plotly_chart(fig2, use_container_width=True)

# ── CHART 3: Product-wise Sales (Pie Chart) ────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Sales by Product")
    product_sales = filtered_df.groupby("Product")["Units_Sold"].sum().reset_index()
    fig3 = px.pie(product_sales, names="Product", values="Units_Sold", title="Units Sold per Product")
    st.plotly_chart(fig3, use_container_width=True)

with col_right:
    st.subheader("Revenue by Product")
    product_rev = filtered_df.groupby("Product")["Revenue"].sum().reset_index()
    fig4 = px.bar(product_rev, x="Product", y="Revenue", color="Product", title="Revenue per Product")
    st.plotly_chart(fig4, use_container_width=True)

# ── RAW DATA TABLE ─────────────────────────────────────────
with st.expander("📋 View Raw Data"):   # collapsed by default, click to expand
    st.dataframe(filtered_df, use_container_width=True)
