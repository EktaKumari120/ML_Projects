import nltk
REQUIRED_RESOURCES = ['punkt_tab', 'stopwords', 'vader_lexicon']
for resource in REQUIRED_RESOURCES:
    try:
        nltk.data.find(resource)
    except LookupError:
        nltk.download(resource)

import re
import string
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# Initialize VADER once — we don't want to reload it every time we analyze
sia = SentimentIntensityAnalyzer()

# Get English stopwords — common words like "the", "is", "at" that carry no meaning
stop_words = set(stopwords.words('english'))


def clean_text(text):
    """
    Takes raw headline/description text and returns a cleaned version.
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Lowercase everything
    text = text.lower()
    
    # Remove URLs (some descriptions contain links)
    text = re.sub(r'http\S+|www\S+', '', text)
    
    # Remove punctuation like . , ! ? etc.
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def get_sentiment_label(compound_score):
    """
    Converts a numeric compound score into a human-readable label.
    """
    if compound_score >= 0.05:
        return 'Positive'
    elif compound_score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'


def extract_keywords(text, top_n=5):
    """
    Extracts the most meaningful words from a text.
    Removes stopwords and short words, returns top N words as a string.
    """
    if not text:
        return ""
    
    # Split text into individual words
    words = word_tokenize(text)
    
    # Keep only meaningful words:
    # - not a stopword (remove "the", "is", "at" etc.)
    # - longer than 2 characters (remove "a", "an", "is")
    # - only actual letters, no numbers or symbols
    keywords = [
        word for word in words
        if word not in stop_words
        and len(word) > 2
        and word.isalpha()
    ]
    
    # Return top N keywords joined as a comma-separated string
    return ', '.join(keywords[:top_n])


def analyze_article(title, description=''):
    """
    Main function — takes a news title and optional description,
    returns a dictionary with all sentiment info.
    
    We combine title + description for better accuracy,
    but we clean them separately first.
    """
    # Clean both parts
    clean_title = clean_text(title)
    clean_desc = clean_text(description)
    
    # Combine them for scoring — title is more important so we use it twice
    combined_text = f"{clean_title} {clean_title} {clean_desc}".strip()
    
    # Get scores from VADER
    scores = sia.polarity_scores(combined_text)
    
    # Build and return a result dictionary
    return {
        'clean_title': clean_title,
        'compound': round(scores['compound'], 4),
        'positive': round(scores['pos'], 4),
        'negative': round(scores['neg'], 4),
        'neutral': round(scores['neu'], 4),
        'sentiment': get_sentiment_label(scores['compound']),
        'keywords': extract_keywords(combined_text)
    }

# if __name__ == "__main__":
#     result = analyze_article(
#         title="Tesla stock surges after record-breaking quarterly profits",
#         description="Investors celebrate as Tesla reports highest revenue in company history."
#     )
#     for key, value in result.items():
#         print(f"{key}: {value}")