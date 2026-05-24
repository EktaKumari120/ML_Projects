import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from data import fetch_stock_data
from model import add_features, train_all_models, smart_ensemble_predict
# ── Page Config ──────────────────────────
st.set_page_config(
    page_title="Stock Dashboard",
    page_icon="📈",
    layout="wide"
)

# ── Header ───────────────────────────────
st.title("📈 AI-Powered Stock Analysis Dashboard")
st.markdown(
    """
    Real-time stock data analysis with **machine learning predictions**.  
    Compare multiple ML models and get intelligent ensemble predictions.
    """
)

st.divider()

# ── Sidebar ──────────────────────────────
st.sidebar.header("⚙️ Settings")

ticker = st.sidebar.text_input(
    "Enter Stock Ticker",
    value="AAPL",
    help="Example: AAPL, TSLA, GOOGL, MSFT"
).upper()

period = st.sidebar.selectbox(
    "Select Time Period",
    options=["1mo", "3mo", "6mo", "1y", "2y", "5y"],
    index=3
)

show_ma = st.sidebar.checkbox("Show Moving Averages", value=True)
show_volume = st.sidebar.checkbox("Show Volume Chart", value=True)

st.sidebar.divider()
st.sidebar.caption("Data sourced from Yahoo Finance")

# ── Fetch Data ────────────────────────────
with st.spinner("Fetching stock data..."):
    df = fetch_stock_data(ticker, period)

if df.empty:
    st.error("No data found. Please check the ticker symbol.")
    st.stop()

st.success(f"Loaded {len(df)} trading days of data for {ticker}")

# Add this right after "Loaded X trading days" success message
with st.expander("📊 Data Summary"):
    st.write(f"**Date Range**: {df['Date'].iloc[0].strftime('%B %d, %Y')} to {df['Date'].iloc[-1].strftime('%B %d, %Y')}")
    st.write(f"**Total Trading Days**: {len(df)}")
    st.write(f"**Highest Price**: ${df['Close'].max():.2f}")
    st.write(f"**Lowest Price**: ${df['Close'].min():.2f}")
    st.write(f"**Average Daily Volume**: {df['Volume'].mean():,.0f} shares")


# ── Quick Stats ───────────────────────────
st.subheader(f"{ticker} — Key Stats")   

current_price = round(df["Close"].iloc[-1], 2)
period_high   = round(df["Close"].max(), 2)
period_low    = round(df["Close"].min(), 2)
first_price   = round(df["Close"].iloc[0], 2)
total_change  = round(((current_price - first_price) / first_price) * 100, 2)
day_change    = round(df["Close"].iloc[-1] - df["Close"].iloc[-2], 2)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Current Price",
        value=f"${current_price}",
        delta=f"${day_change} today"
    )

with col2:
    st.metric(
        label="Period High",
        value=f"${period_high}"
    )

with col3:
    st.metric(
        label="Period Low",
        value=f"${period_low}"
    )

with col4:
    st.metric(
        label="Total Change",
        value=f"{total_change}%",
        delta=f"since {df['Date'].iloc[0].strftime('%b %Y')}"
    )

# ── Price Chart ───────────────────────────
st.subheader("📈 Price Chart")

df_feat = add_features(df)

fig = go.Figure()

# closing price line
fig.add_trace(go.Scatter(
    x=df["Date"],
    y=df["Close"],
    name="Close Price",
    line=dict(color="#00b4d8", width=2.5)
))

# MA_7 line (only if show_ma is True)
if show_ma:
    fig.add_trace(go.Scatter(
        x=df_feat["Date"],
        y=df_feat["MA_7"],
        name="7-Day MA",
        line=dict(color="#f77f00",width = 1, dash="dash")
    ))
    
    # MA_21 line
    fig.add_trace(go.Scatter(
        x=df_feat["Date"],
        y=df_feat["MA_21"],
        name="21-Day MA",
        line=dict(color="#d62828",width = 1, dash="dot")
    ))

fig.update_layout(
    template="plotly_dark",
    xaxis_title="Date",
    yaxis_title="Price (USD)",
    hovermode="x unified",
    height=500,
    xaxis=dict(
        rangeslider=dict(visible=True),
    )
)

st.plotly_chart(fig, use_container_width=True)

# ── Volume Chart ─────────────────────────
if show_volume:
    st.subheader("📦 Trading Volume")
    
    vol_fig = px.bar(
        df,
        x="Date",
        y="Volume",
        title="Daily Trading Volume",
        color_discrete_sequence=["#48cae4"]
    )
    
    vol_fig.update_layout(
        template="plotly_dark",
        xaxis_title="Date",
        yaxis_title="Volume",
        height=300
    )
    
    st.plotly_chart(vol_fig, use_container_width=True)

st.divider()

st.divider()

# ── ML Prediction Section ────────────────────────
st.header("🤖 Machine Learning Predictions")

# Train models

if len(df_feat) < 30:
    st.warning("Not enough data for ML. Choose a longer time period.")
else:
    with st.spinner("Training models..."):
        trained_models, results, all_predictions, X_test, y_test = train_all_models(df_feat)
        final_prediction, models_used, method = smart_ensemble_predict(trained_models, results, df_feat)
    
    # Model Comparison Chart
    st.subheader("📊 Model Performance Comparison")
    
    results_df = pd.DataFrame({
        "Model": list(results.keys()),
        "MAE ($)": list(results.values())
    })
    
    # Create bar chart with color coding - best model in green
    best_model = results_df.loc[results_df["MAE ($)"].idxmin(), "Model"]
    colors = ["#10b981" if model == best_model else "#6366f1" 
              for model in results_df["Model"]]
    
    bar_fig = px.bar(
        results_df,
        x="Model",
        y="MAE ($)",
        title="Lower MAE = Better Model",
        color="Model",
        color_discrete_sequence=colors
    )
    
    bar_fig.update_layout(
        template="plotly_dark",
        showlegend=False,
        height=400
    )
    
    st.plotly_chart(bar_fig, use_container_width=True)
    
    # Prediction Display
    st.subheader("🎯 Final Prediction")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Current Price",
            value=f"${current_price}"
        )
    
    with col2:
        difference = round(final_prediction - current_price, 2)
        st.metric(
            label="Predicted Next Day",
            value=f"${final_prediction}",
            delta=f"${difference}"
        )
    
    with col3:
        st.metric(
            label="Prediction Method",
            value=method
        )
    
    # Show which models were used
    with st.expander("📋 Models Used in Prediction"):
        for name, pred in models_used.items():
            st.write(f"**{name}**: ${pred:.2f}")
    
    # Actual vs Predicted Chart
    st.subheader("📈 Actual vs Predicted (Test Set)")
    
    # Get the best model's predictions for the chart
    best_model_preds = all_predictions[best_model]
    
    comparison_fig = go.Figure()
    
    comparison_fig.add_trace(go.Scatter(
        y=y_test.values,
        name="Actual Price",
        line=dict(color="#10b981", width=2)
    ))
    
    comparison_fig.add_trace(go.Scatter(
        y=best_model_preds,
        name=f"{best_model} Prediction",
        line=dict(color="#ef4444", width=2, dash="dash")
    ))
    
    comparison_fig.update_layout(
        template="plotly_dark",
        xaxis_title="Test Days",
        yaxis_title="Price (USD)",
        hovermode="x unified",
        height=400
    )
    
    st.plotly_chart(comparison_fig, use_container_width=True)
    
    st.info(f"💡 The {best_model} achieved MAE of ${results[best_model]:.2f}, meaning on average it was off by only ${results[best_model]:.2f} per prediction.")

## Download
st.divider()
st.subheader("💾 Download Data")

col1, col2 = st.columns(2)

with col1:
    # Download raw stock data
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Stock Data (CSV)",
        data=csv_data,
        file_name=f"{ticker}_stock_data.csv",
        mime="text/csv"
    )

with col2:
    # Download featured data
    csv_feat = df_feat.to_csv(index=False)
    st.download_button(
        label="📥 Download Featured Data (CSV)",
        data=csv_feat,
        file_name=f"{ticker}_featured_data.csv",
        mime="text/csv"
    )

# Disclaimer
st.divider()
st.caption("⚠️ **Disclaimer**: This dashboard is for educational purposes only. Stock predictions are based on historical patterns and do not account for news, earnings reports, or market events. Not financial advice.")