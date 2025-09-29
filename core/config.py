"""
Configuration settings for NewsCast AI
"""

# --- API Keys & Credentials ---
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "your_groq_api_key_here")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your_openai_api_key_here")

# Twitter API credentials (optional)
TWITTER_API_KEY = "your_twitter_api_key"
TWITTER_API_SECRET = "your_twitter_api_secret"
TWITTER_ACCESS_TOKEN = "your_twitter_access_token"
TWITTER_ACCESS_SECRET = "your_twitter_access_secret"
TWITTER_BEARER_TOKEN = "your_twitter_bearer_token"

# --- Episode Generation Settings ---
DEFAULT_SEGMENTS = 8  # Standard 8 segments instead of 20
DEFAULT_DURATION = 35  # minutes
DEFAULT_ARTICLES = 25  # Reduced for faster processing

# --- Enhanced News Categories ---
NEWS_CATEGORIES = {
    "politics": {
        "conservative": [
            "Fox News", "The Hill", "Breitbart", "Daily Wire", "Newsmax", "The Federalist", "National Review"
        ],
        "liberal": [
            "CNN", "MSNBC", "HuffPost", "Vox", "The Atlantic", "Mother Jones", "The Nation", "Slate"
        ],
        "neutral": [
            "Reuters", "Associated Press", "BBC News", "NPR", "PBS", "Politico", "The Hill", "Axios"
        ],
        "international": [
            "BBC News", "Deutsche Welle", "France 24", "Al Jazeera", "RT News", "Sputnik"
        ]
    },
    "scope": {
        "local": [
            "Local News", "Regional News", "State News", "City News"
        ],
        "national": [
            "USA Today", "New York Times", "Washington Post", "Wall Street Journal", "Los Angeles Times", "Chicago Tribune"
        ],
        "global": [
            "BBC News", "Reuters", "Al Jazeera", "Deutsche Welle", "France 24", "DW News", "Euronews"
        ],
        "regional": [
            "European News", "Asian News", "African News", "Latin American News", "Middle East News"
        ]
    },
    "topics": {
        "technology": [
            "TechCrunch", "Ars Technica", "The Verge", "Wired", "Engadget", "Gizmodo", "Mashable"
        ],
        "business": [
            "Bloomberg", "Financial Times", "Wall Street Journal", "Fortune", "Business Insider", "Forbes"
        ],
        "science": [
            "Nature", "Science Magazine", "Scientific American", "New Scientist", "Popular Science"
        ],
        "health": [
            "WebMD", "Mayo Clinic", "Healthline", "Medical News Today", "CDC", "WHO"
        ],
        "sports": [
            "ESPN", "Sports Illustrated", "The Athletic", "Bleacher Report", "Yahoo Sports"
        ],
        "entertainment": [
            "Entertainment Weekly", "Variety", "The Hollywood Reporter", "Rolling Stone", "Billboard"
        ],
        "environment": [
            "Environmental News Network", "Climate Central", "Greenpeace", "Sierra Club"
        ],
        "education": [
            "Education Week", "Chronicle of Higher Education", "Inside Higher Ed"
        ],
        "lifestyle": [
            "People", "Real Simple", "Good Housekeeping", "Martha Stewart"
        ],
        "finance": [
            "MarketWatch", "Yahoo Finance", "CNBC", "Investopedia", "Morningstar"
        ],
        "automotive": [
            "Motor Trend", "Car and Driver", "Road & Track", "Automotive News"
        ],
        "travel": [
            "Travel + Leisure", "National Geographic Travel", "Lonely Planet", "Condé Nast Traveler"
        ]
    }
}

# --- RSS Feed Sources ---
RSS_FEEDS = {
    "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    "Reuters": "http://feeds.reuters.com/reuters/topNews",
    "Associated Press": "https://feeds.apnews.com/rss/apf-topnews",
    "CNN": "http://rss.cnn.com/rss/edition.rss",
    "NPR": "https://feeds.npr.org/1001/rss.xml",
    "The Guardian": "https://www.theguardian.com/world/rss",
    "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "Deutsche Welle": "https://rss.dw.com/xml/rss-en-all",
    "France 24": "https://www.france24.com/en/rss",
    "TechCrunch": "https://techcrunch.com/feed/",
    "Ars Technica": "http://feeds.arstechnica.com/arstechnica/index",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Wired": "https://www.wired.com/feed/rss",
    "Engadget": "https://www.engadget.com/rss.xml",
    "Gizmodo": "https://gizmodo.com/rss",
    "Mashable": "https://mashable.com/feeds/rss/all",
    "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
    "Financial Times": "https://www.ft.com/rss/home",
    "Wall Street Journal": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    "Fortune": "https://fortune.com/feed/",
    "Business Insider": "https://feeds.businessinsider.com/custom/all",
    "Forbes": "https://www.forbes.com/real-time/feed2/",
    "ESPN": "https://www.espn.com/espn/rss/news",
    "Variety": "https://variety.com/feed/",
    "Rolling Stone": "https://www.rollingstone.com/feed/"
}

# --- Web Scraping Sources ---
WEB_SOURCES = [
    {
        "name": "Wikipedia Current Events",
        "url": "https://en.wikipedia.org/wiki/Portal:Current_events",
        "selector": ".vevent"
    }
]

# --- Audio Settings ---
AUDIO_SETTINGS = {
    "fast_mode": {
        "bitrate": "128k",
        "sample_rate": "22050",
        "channels": "1",  # Mono
        "quality": "4"
    },
    "high_quality": {
        "bitrate": "192k", 
        "sample_rate": "44100",
        "channels": "2",  # Stereo
        "quality": "2"
    }
}
