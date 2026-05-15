from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.orm import declarative_base, Session
from datetime import datetime
import pandas as pd

# This creates a local SQLite file called news_sentiment.db in your project folder
# The 'sqlite:///' part tells SQLAlchemy what kind of database to use
ENGINE = create_engine('sqlite:///news_sentiment.db', echo=False)

# Base is the parent class all our database models will inherit from
Base = declarative_base()


class Article(Base):
    """
    This class defines the structure of our 'articles' table.
    Each attribute = one column in the database.
    """
    __tablename__ = 'articles'

    id            = Column(Integer, primary_key=True, autoincrement=True)
    title         = Column(String, nullable=False)
    source        = Column(String)
    published_at  = Column(String)   # stored as string YYYY-MM-DD
    url           = Column(String)
    query         = Column(String)   # what search term was used
    sentiment     = Column(String)   # Positive / Negative / Neutral
    compound      = Column(Float)
    positive      = Column(Float)
    negative      = Column(Float)
    neutral       = Column(Float)
    keywords      = Column(String)
    fetched_at    = Column(DateTime, default=datetime.now)  # when WE fetched it


def init_db():
    """
    Creates the database and tables if they don't exist yet.
    Safe to call multiple times — won't overwrite existing data.
    """
    Base.metadata.create_all(ENGINE)
    print("Database ready.")


def save_articles(df):
    """
    Takes a DataFrame of articles and saves them to the database.
    Skips duplicates — if the same article title already exists, we don't insert it again.
    """
    if df.empty:
        print("No articles to save.")
        return 0

    # Get titles already in the database so we can skip them
    existing_titles = get_existing_titles()

    saved_count = 0

    with Session(ENGINE) as session:
        for _, row in df.iterrows():

            # Skip if this article is already saved
            if row['title'] in existing_titles:
                continue

            article = Article(
                title        = row['title'],
                source       = row.get('source', ''),
                published_at = str(row.get('published_at', ''))[:10],
                url          = row.get('url', ''),
                query        = row.get('query', ''),
                sentiment    = row.get('sentiment', ''),
                compound     = row.get('compound', 0.0),
                positive     = row.get('positive', 0.0),
                negative     = row.get('negative', 0.0),
                neutral      = row.get('neutral', 0.0),
                keywords     = row.get('keywords', ''),
                fetched_at   = datetime.now()
            )
            session.add(article)
            saved_count += 1

        session.commit()

    print(f"Saved {saved_count} new articles to database.")
    return saved_count


def get_existing_titles():
    """
    Returns a set of article titles already in the database.
    We use a set because checking 'if x in set' is very fast.
    """
    with Session(ENGINE) as session:
        # text() tells SQLAlchemy we're writing raw SQL — fine for simple queries
        result = session.execute(text("SELECT title FROM articles")).fetchall()
        return {row[0] for row in result}


def load_all_articles():
    """
    Loads everything from the database and returns it as a DataFrame.
    This is what the dashboard will call to get data.
    """
    with Session(ENGINE) as session:
        result = session.execute(text("SELECT * FROM articles ORDER BY fetched_at DESC")).fetchall()
        columns = ['id', 'title', 'source', 'published_at', 'url', 'query',
                   'sentiment', 'compound', 'positive', 'negative', 'neutral',
                   'keywords', 'fetched_at']
        df = pd.DataFrame(result, columns=columns)

    if not df.empty:
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')
        df['fetched_at'] = pd.to_datetime(df['fetched_at'], errors='coerce')

    return df


def load_by_query(query):
    """
    Loads only articles matching a specific search term.
    Useful for filtering dashboard by topic.
    """
    with Session(ENGINE) as session:
        result = session.execute(
            text("SELECT * FROM articles WHERE query = :q ORDER BY published_at DESC"),
            {"q": query}
        ).fetchall()

        columns = ['id', 'title', 'source', 'published_at', 'url', 'query',
                   'sentiment', 'compound', 'positive', 'negative', 'neutral',
                   'keywords', 'fetched_at']
        df = pd.DataFrame(result, columns=columns)

    if not df.empty:
        df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')

    return df


def get_all_queries():
    """
    Returns a list of all unique search terms ever used.
    The dashboard uses this to populate a dropdown filter.
    """
    with Session(ENGINE) as session:
        result = session.execute(
            text("SELECT DISTINCT query FROM articles ORDER BY query")
        ).fetchall()
        return [row[0] for row in result]


def get_sentiment_summary():
    """
    Returns a count of Positive / Negative / Neutral articles overall.
    Used for the summary cards at the top of the dashboard.
    """
    with Session(ENGINE) as session:
        result = session.execute(
            text("SELECT sentiment, COUNT(*) as count FROM articles GROUP BY sentiment")
        ).fetchall()
        return {row[0]: row[1] for row in result}
    

# if __name__ == "__main__":
#     # Step 1: create the database
#     init_db()

#     # Step 2: load the CSV we saved in Step 3 and save it to DB
#     df = pd.read_csv('data/news_data.csv')
#     save_articles(df)

#     # Step 3: load it back and check
#     all_articles = load_all_articles()
#     print(f"\nTotal articles in DB: {len(all_articles)}")
#     print(all_articles[['title', 'sentiment', 'compound']].head())

#     # Step 4: check summary
#     summary = get_sentiment_summary()
#     print(f"\nSentiment breakdown: {summary}")