# News Sentiment Analysis Dashboard

## Business Problem
Understand the overall tone (positive/negative/neutral) of current news 
coverage on a given topic, without manually reading through dozens of articles.

## Approach
- Fetched live headlines using the NewsAPI
- Applied sentiment analysis using NLTK's VADER (rule-based NLP sentiment scoring)
- Stored articles and sentiment scores in a SQLite database via SQLAlchemy
- Built a Streamlit dashboard with Plotly charts and word clouds to visualize sentiment trends over time

## Tools & Libraries
Python, Streamlit, NLTK (VADER), NewsAPI, SQLite, SQLAlchemy, Plotly, WordCloud, Pandas

## Key Insight
Aggregating sentiment across many headlines reveals overall media tone 
on a topic more reliably than reading any single article in isolation.

## Files
- Streamlit app script
- SQLite database file