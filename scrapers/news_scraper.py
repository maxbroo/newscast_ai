"""
News scraping functionality for NewsCast AI
"""

import feedparser
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
import random
import time
from typing import List, Dict, Any
from urllib.parse import urljoin, urlparse

from core.config import RSS_FEEDS, WEB_SOURCES, NEWS_CATEGORIES
from utils.logging_config import get_logger

logger = get_logger(__name__)

class NewsScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def gather_news_with_categories(self, categories: Dict[str, List[str]], max_articles: int = 25) -> List[Dict[str, Any]]:
        """Gather news articles based on specified categories"""
        logger.info("Gathering news from RSS feeds and web scraping...")
        
        all_articles = []
        
        # Scrape RSS feeds
        for source_name, feed_url in RSS_FEEDS.items():
            try:
                articles = self._scrape_rss_feed(feed_url, source_name)
                all_articles.extend(articles)
                logger.info(f"Scraped {len(articles)} articles from {source_name}")
                time.sleep(1)  # Be respectful to servers
            except Exception as e:
                logger.error(f"Error fetching from {source_name}: {e}")
        
        # Scrape web sources
        for source in WEB_SOURCES:
            try:
                articles = self._scrape_web_source(source)
                all_articles.extend(articles)
                logger.info(f"Scraped {len(articles)} articles from {source['name']}")
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error scraping {source['name']}: {e}")
        
        # Filter and categorize articles
        filtered_articles = self._filter_and_categorize_articles(all_articles, categories)
        
        # Limit articles and shuffle for variety
        if len(filtered_articles) > max_articles:
            filtered_articles = random.sample(filtered_articles, max_articles)
        
        # Save articles to file
        self._save_articles_to_file(filtered_articles)
        
        logger.info(f"Found {len(filtered_articles)} articles from {len(set(a['source'] for a in filtered_articles))} sources")
        return filtered_articles

    def _scrape_rss_feed(self, feed_url: str, source_name: str) -> List[Dict[str, Any]]:
        """Scrape articles from RSS feed"""
        articles = []
        
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # Limit per source
                article = {
                    "title": entry.get('title', 'No Title'),
                    "summary": entry.get('summary', entry.get('description', 'No Summary')),
                    "link": entry.get('link', ''),
                    "published": entry.get('published', ''),
                    "source": source_name,
                    "scraped_at": datetime.now().isoformat()
                }
                
                # Clean HTML from summary
                if article['summary']:
                    soup = BeautifulSoup(article['summary'], 'html.parser')
                    article['summary'] = soup.get_text().strip()
                
                articles.append(article)
                
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {e}")
            
        return articles

    def _scrape_web_source(self, source: Dict[str, str]) -> List[Dict[str, Any]]:
        """Scrape articles from web source"""
        articles = []
        
        try:
            response = self.session.get(source['url'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            elements = soup.select(source['selector'])
            
            for element in elements[:5]:  # Limit per source
                title = element.get_text().strip()
                if title and len(title) > 10:
                    article = {
                        "title": title,
                        "summary": title,  # Use title as summary for web scraped content
                        "link": source['url'],
                        "published": datetime.now().isoformat(),
                        "source": source['name'],
                        "scraped_at": datetime.now().isoformat()
                    }
                    articles.append(article)
                    
        except Exception as e:
            logger.error(f"Error scraping {source['url']}: {e}")
            
        return articles

    def _filter_and_categorize_articles(self, articles: List[Dict[str, Any]], categories: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """Filter and categorize articles based on user preferences"""
        filtered_articles = []
        
        for article in articles:
            # Add category based on source and content
            article['category'] = self._categorize_article(
                article['title'], 
                article['summary'], 
                article['source']
            )
            
            # Check if article matches user categories
            if self._matches_categories(article, categories):
                filtered_articles.append(article)
        
        return filtered_articles

    def _categorize_article(self, title: str, summary: str, source: str) -> str:
        """Categorize an article based on its content and source"""
        text = f"{title} {summary}".lower()
        
        # Check for technology keywords
        tech_keywords = ['ai', 'artificial intelligence', 'tech', 'software', 'app', 'digital', 'cyber', 'data', 'algorithm', 'robot', 'automation', 'blockchain', 'cryptocurrency']
        if any(keyword in text for keyword in tech_keywords):
            return "technology"
        
        # Check for business keywords
        business_keywords = ['business', 'economy', 'market', 'stock', 'financial', 'company', 'corporate', 'revenue', 'profit', 'investment', 'trade']
        if any(keyword in text for keyword in business_keywords):
            return "business"
        
        # Check for politics keywords
        politics_keywords = ['politics', 'government', 'election', 'president', 'congress', 'senate', 'policy', 'law', 'court', 'vote', 'campaign']
        if any(keyword in text for keyword in politics_keywords):
            return "politics"
        
        # Check for health keywords
        health_keywords = ['health', 'medical', 'disease', 'vaccine', 'hospital', 'doctor', 'patient', 'treatment', 'drug', 'medicine']
        if any(keyword in text for keyword in health_keywords):
            return "health"
        
        # Check for sports keywords
        sports_keywords = ['sport', 'game', 'team', 'player', 'match', 'championship', 'league', 'football', 'basketball', 'soccer', 'baseball']
        if any(keyword in text for keyword in sports_keywords):
            return "sports"
        
        # Check for science keywords
        science_keywords = ['science', 'research', 'study', 'discovery', 'experiment', 'climate', 'environment', 'space', 'nasa']
        if any(keyword in text for keyword in science_keywords):
            return "science"
        
        # Check for entertainment keywords
        entertainment_keywords = ['movie', 'film', 'music', 'celebrity', 'actor', 'singer', 'entertainment', 'hollywood', 'album', 'concert']
        if any(keyword in text for keyword in entertainment_keywords):
            return "entertainment"
        
        return "general"

    def _matches_categories(self, article: Dict[str, Any], categories: Dict[str, List[str]]) -> bool:
        """Check if article matches user-specified categories"""
        # If no specific topics are selected, include all articles
        if not categories.get('topics'):
            return True
        
        # Check if article category matches selected topics
        return article['category'] in categories.get('topics', [])

    def _save_articles_to_file(self, articles: List[Dict[str, Any]]):
        """Save articles to JSON file for debugging"""
        filename = f"articles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(articles, f, indent=2, ensure_ascii=False)
            logger.info(f"Successfully saved {len(articles)} articles to {filename}")
        except Exception as e:
            logger.error(f"Error saving articles to file: {e}")

    def process_custom_prompt(self, prompt: str) -> Dict[str, List[str]]:
        """Process custom user prompt to determine news categories using AI"""
        from groq import Groq
        from core.config import GROQ_API_KEY
        
        try:
            client = Groq(api_key=GROQ_API_KEY)
            
            system_prompt = """You are a news categorization AI. Based on the user's request, determine what types of news they want.

Available categories:
- politics (conservative, liberal, neutral, international)
- scope (local, national, global, regional)  
- topics (technology, business, science, health, sports, entertainment, environment, education, lifestyle, finance, automotive, travel)

Return a JSON object with the categories that match their request. Example:
{
  "politics": ["neutral"],
  "scope": ["global"],
  "topics": ["technology", "business"]
}"""
            
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"I want news about: {prompt}"}
                ],
                model="llama3-8b-8192",
                temperature=0.1
            )
            
            # Parse the AI response
            ai_response = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            import re
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                categories = json.loads(json_match.group())
                logger.info(f"AI categorized prompt '{prompt}' as: {categories}")
                return categories
            else:
                # Fallback to general categories
                logger.warning(f"Could not parse AI response for prompt: {prompt}")
                return {"topics": ["technology", "business", "politics"]}
                
        except Exception as e:
            logger.error(f"Error processing custom prompt with AI: {e}")
            # Fallback to general categories
            return {"topics": ["technology", "business", "politics"]}
