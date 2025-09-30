"""
Main episode generation orchestrator for NewsCast AI
"""

from typing import Dict, List, Any

from scrapers.news_scraper import NewsScraper
from generators.script_generator import create_multiple_script_segments
from generators.audio_generator import generate_multiple_segments_audio, combine_all_segments
from utils.file_utils import get_next_episode_number, create_episode_folder, save_episode_metadata
from core.config import DEFAULT_DURATION, DEFAULT_ARTICLES
from utils.logging_config import get_logger

logger = get_logger(__name__)

def generate_new_enhanced_episode(categories: Dict[str, List[str]] = None, 
                                target_duration: int = DEFAULT_DURATION,
                                custom_prompt: str = None) -> str:
    """Generate a new enhanced episode with multiple segments approach"""
    logger.info("Starting enhanced episode generation with 8 segments...")
    
    # Get next episode number and create folder
    episode_number = get_next_episode_number()
    episode_folder = create_episode_folder(episode_number)
    logger.info(f"Creating Episode {episode_number} in folder: {episode_folder}")
    
    # Initialize scraper and gather news
    scraper = NewsScraper()
    
    # If custom prompt is provided, use AI to determine categories
    if custom_prompt:
        logger.info(f"Processing custom prompt: {custom_prompt}")
        categories = scraper.process_custom_prompt(custom_prompt)
        logger.info(f"AI determined categories: {categories}")
    
    # Use default categories if none provided
    if not categories:
        categories = {
            'politics': ['neutral'],
            'scope': ['global'],
            'topics': ['technology', 'business']
        }
    
    articles = scraper.gather_news_with_categories(categories, max_articles=DEFAULT_ARTICLES)
    
    if not articles:
        logger.error("No articles found. Aborting.")
        return None
    
    # Create multiple script segments (8 segments standard)
    segments = create_multiple_script_segments(articles, target_duration)
    if not segments:
        logger.error("Script segments generation failed. Aborting.")
        return None
    
    # Generate audio for all segments
    audio_files = generate_multiple_segments_audio(segments, episode_folder)
    
    # Combine all segments into final episode
    combined_audio = combine_all_segments(episode_folder, episode_number)
    
    # Save metadata
    save_episode_metadata(episode_folder, episode_number, segments, articles, audio_files, combined_audio)
    
    logger.info(f"✅ Enhanced Episode {episode_number} ready with {len(segments)} segments!")
    return episode_folder
