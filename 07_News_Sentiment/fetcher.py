import requests
import pandas as pd
from datetime import datetime, timedelta
from analyzer import analyze_article

API_KEY = "7e17cd37c6764f68bfec122c399a7790"
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_news(query="technology", days_back=1, max_articles=30):
    """
    Fetches news articles from NewsAPI for a given search query.
    
    query       — what topic to search e.g. "bitcoin", "climate", "india"
    days_back   — how many days back to fetch (free plan supports up to 1 month)
    max_articles — how many articles to return (free plan max is 100)
    """
    
    from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    params = {
        'q': query,
        'from': from_date,
        'sortBy': 'publishedAt',   # newest articles first
        'language': 'en',
        'pageSize': max_articles,
        'apiKey': API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=10)

        # If the API returns an error status (like 401 wrong key, 429 rate limit)
        # this will raise an exception so we catch it below
        response.raise_for_status()

        data = response.json()

        # 'articles' is the list of news items inside the API response
        articles = data.get('articles', [])
        
        if not articles:
            print(f"No articles found for query: {query}")
            return pd.DataFrame()

        return process_articles(articles, query)
    
    except requests.exceptions.ConnectionError:
        print("No internet connection. Try using load_sample_data() instead.")
        return pd.DataFrame()
    
    except requests.exceptions.HTTPError as e:
        print(f"API error: {e}")
        return pd.DataFrame()
    
    except Exception as e:
        print(f"Something went wrong: {e}")
        return pd.DataFrame()

def process_articles(articles, query):
    """
    Takes the raw list of article dicts from NewsAPI
    and turns them into a clean DataFrame with sentiment scores.
    """
    rows = []
    for article in articles:
        # Some articles come with None values — we handle that safely
        title = article.get('title') or ''
        description = article.get('description') or ''
        source = article.get('source', {}).get('name') or 'Unknown'
        published_at = article.get('publishedAt') or ''
        url = article.get('url') or ''
    
        # Skip articles that have no title — they're useless
        if not title or title == '[Removed]':
            continue

        # Run our analyzer on this article
        analysis = analyze_article(title, description)
        
        # Build one row combining article info + sentiment results
        rows.append({
            'title': title,
            'source': source,
            'published_at': published_at[:10],  # keep only YYYY-MM-DD part
            'url': url,
            'query': query,
            'sentiment': analysis['sentiment'],
            'compound': analysis['compound'],
            'positive': analysis['positive'],
            'negative': analysis['negative'],
            'neutral': analysis['neutral'],
            'keywords': analysis['keywords']
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    # Convert published_at to proper datetime so we can sort/filter by date
    df['published_at'] = pd.to_datetime(df['published_at'])

    # Sort newest first
    df = df.sort_values('published_at', ascending=False).reset_index(drop=True)

    return df

def load_sample_data():
    """
    Offline fallback — loads from a CSV file.
    Useful when you've already fetched and saved data before.
    """
    try:
        df = pd.read_csv('data/news_data.csv')
        df['published_at'] = pd.to_datetime(df['published_at'])
        print(f"Loaded {len(df)} articles from saved CSV.")
        return df
    except FileNotFoundError:
        print("No saved data found. Please fetch from API first.")
        return pd.DataFrame()
    
def save_data(df, filename='data/news_data.csv'):
    """
    Saves the fetched DataFrame to CSV so we can reload it later
    without hitting the API again.
    """
    if df.empty:
        print("Nothing to save.")
        return
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} articles to {filename}")

# if __name__ == "__main__":
#     df = fetch_news(query="artificial intelligence", days_back=1, max_articles=5)
    
#     if not df.empty:
#         print(f"\nFetched {len(df)} articles\n")
#         print(df[['title', 'sentiment', 'compound']].to_string())
#         save_data(df)
