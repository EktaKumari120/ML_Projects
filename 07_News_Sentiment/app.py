import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from fetcher import fetch_news, save_data
from database import init_db, save_articles, load_all_articles, load_by_query, get_all_queries, get_sentiment_summary

# ─── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="News Sentiment Analyzer",
    page_icon="📰",
    layout="wide"
)

# Initialize database on every run — safe because it won't overwrite existing data
init_db()

# ─── Title ──────────────────────────────────────────────────────────────────
st.title("📰 News Sentiment Analyzer")
st.caption("Fetch live news headlines and analyze their sentiment in real time.")

# ─── Sidebar: Fetch new articles ────────────────────────────────────────────
st.sidebar.header("🔍 Fetch News")

query = st.sidebar.text_input("Search topic", value="technology")
days_back = st.sidebar.slider("Days back", min_value=1, max_value=7, value=1)
max_articles = st.sidebar.slider("Max articles", min_value=5, max_value=50, value=20)

if st.sidebar.button("Fetch & Analyze"):
    with st.spinner(f"Fetching news about '{query}'..."):
        df_new = fetch_news(query=query, days_back=days_back, max_articles=max_articles)

    if df_new.empty:
        st.sidebar.error("No articles found. Try a different topic.")
    else:
        save_data(df_new)           # save to CSV
        save_articles(df_new)       # save to SQLite
        st.sidebar.success(f"Fetched {len(df_new)} articles!")

# ─── Sidebar: Filter by topic ────────────────────────────────────────────────
st.sidebar.header("🗂️ Filter by Topic")

all_queries = get_all_queries()

if all_queries:
    selected_query = st.sidebar.selectbox("Topic", options=["All"] + all_queries)
else:
    selected_query = "All"

# ─── Load data ───────────────────────────────────────────────────────────────
if selected_query == "All":
    df = load_all_articles()
else:
    df = load_by_query(selected_query)

# ─── Empty state ─────────────────────────────────────────────────────────────
if df.empty:
    st.info("No data yet. Use the sidebar to fetch some news articles first.")
    st.stop()   # stop rendering the rest of the dashboard until we have data

# ─── Summary cards ───────────────────────────────────────────────────────────
st.subheader("📊 Overview")

total     = len(df)
positive  = len(df[df['sentiment'] == 'Positive'])
negative  = len(df[df['sentiment'] == 'Negative'])
neutral   = len(df[df['sentiment'] == 'Neutral'])
avg_score = df['compound'].mean()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Articles", total)
col2.metric("Positive 😊", positive)
col3.metric("Negative 😟", negative)
col4.metric("Neutral 😐", neutral)
col5.metric("Avg Compound", f"{avg_score:.3f}")

st.divider()

# ─── Charts row ──────────────────────────────────────────────────────────────
st.subheader("📈 Sentiment Breakdown")

left, right = st.columns(2)

with left:
    # Pie chart — overall sentiment distribution
    sentiment_counts = df['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']

    color_map = {
        'Positive': '#2ecc71',
        'Negative': '#e74c3c',
        'Neutral':  '#95a5a6'
    }

    fig_pie = px.pie(
        sentiment_counts,
        names='Sentiment',
        values='Count',
        color='Sentiment',
        color_discrete_map=color_map,
        title='Sentiment Distribution'
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with right:
    df_bar = df.head(10).copy()
    df_bar['short_title'] = df_bar['title'].str[:35] + '...'

    fig_bar = px.bar(
        df_bar,
        x='compound',
        y='short_title',
        orientation='h',
        color='compound',
        color_continuous_scale=['#e74c3c', '#95a5a6', '#2ecc71'],
        range_color=[-1, 1],
        title='Compound Score — Latest 10 Articles',
        labels={'compound': 'Score', 'short_title': ''}
    )
    fig_bar.update_layout(
        yaxis=dict(autorange='reversed'),
        height=420,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(size=11)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ─── Trend line ──────────────────────────────────────────────────────────────
st.subheader("📅 Sentiment Over Time")

# Group articles by date and calculate average compound score per day
df_trend = (
    df.groupby('published_at')['compound']
    .mean()
    .reset_index()
    .sort_values('published_at')
)

fig_line = px.line(
    df_trend,
    x='published_at',
    y='compound',
    markers=True,
    title='Average Sentiment Score by Date',
    labels={'published_at': 'Date', 'compound': 'Avg Compound Score'}
)

# Add a horizontal line at 0 so positive/negative split is clear
fig_line.add_hline(y=0, line_dash='dash', line_color='gray', opacity=0.5)
fig_line.update_traces(line_color='#3498db')
st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# ─── Word cloud ──────────────────────────────────────────────────────────────
st.subheader("☁️ Keyword Word Cloud")

# Combine all keywords from all articles into one big string
all_keywords = ' '.join(df['keywords'].dropna().tolist())

if all_keywords.strip():
    wordcloud = WordCloud(
        width=900,
        height=400,
        background_color='white',
        colormap='RdYlGn',       # red = less frequent, green = more frequent
        max_words=80,
        collocations=False       # don't repeat word pairs
    ).generate(all_keywords)

    fig_wc, ax = plt.subplots(figsize=(12, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.pyplot(fig_wc)
else:
    st.info("Not enough keywords to generate a word cloud yet.")

st.divider()

# ─── Source breakdown ─────────────────────────────────────────────────────────
st.subheader("📰 Articles by Source")

source_counts = df['source'].value_counts().head(10).reset_index()
source_counts.columns = ['Source', 'Count']

fig_source = px.bar(
    source_counts,
    x='Source',
    y='Count',
    color='Count',
    color_continuous_scale='Blues',
    title='Top 10 News Sources'
)
st.plotly_chart(fig_source, use_container_width=True)

st.divider()

# ─── Article table ────────────────────────────────────────────────────────────
st.subheader("📋 All Articles")

# Sentiment filter above the table
sentiment_filter = st.selectbox(
    "Filter by sentiment",
    options=["All", "Positive", "Negative", "Neutral"]
)

df_display = df.copy()
if sentiment_filter != "All":
    df_display = df_display[df_display['sentiment'] == sentiment_filter]

# Show clean columns only
st.dataframe(
    df_display[['title', 'source', 'published_at', 'sentiment', 'compound', 'keywords']],
    use_container_width=True,
    hide_index=True,
    column_config={
        "compound": st.column_config.NumberColumn("Score", format="%.3f"),
        "published_at": st.column_config.DateColumn("Date"),
    }
)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.caption("Data sourced from NewsAPI · Sentiment powered by VADER · Built with Streamlit")