"""
Script generation functionality for NewsCast AI
"""

from groq import Groq
from typing import List, Dict, Any
import random

from core.config import GROQ_API_KEY, DEFAULT_SEGMENTS
from utils.logging_config import get_logger

logger = get_logger(__name__)

def create_multiple_script_segments(articles: List[Dict[str, Any]], target_duration_minutes: int = 35) -> List[Dict[str, Any]]:
    """Create multiple smaller script segments that can be combined into a longer episode"""
    logger.info(f"Creating multiple script segments targeting {target_duration_minutes} minutes...")
    
    # Use 8 segments as standard (much better than 20!)
    num_segments = DEFAULT_SEGMENTS
    segment_duration = target_duration_minutes / num_segments  # Each segment ~4-5 minutes
    
    # Group articles by category
    categorized_articles = {}
    for article in articles:
        category = article.get("category", "general")
        if category not in categorized_articles:
            categorized_articles[category] = []
        categorized_articles[category].append(article)
    
    # Create a flat list of all articles
    all_articles = []
    for category, cat_articles in categorized_articles.items():
        all_articles.extend(cat_articles)
    
    # Shuffle for variety
    random.shuffle(all_articles)
    
    # Create segments with 2-3 articles each
    segments = []
    articles_per_segment = max(1, len(all_articles) // num_segments)
    
    for i in range(num_segments):
        start_idx = i * articles_per_segment
        end_idx = min(start_idx + articles_per_segment + 1, len(all_articles))  # +1 for slight overlap
        
        if start_idx >= len(all_articles):
            break
            
        segment_articles = all_articles[start_idx:end_idx]
        if segment_articles:
            segment_title = f"Segment {i+1}: {segment_articles[0].get('category', 'News').title()} Update"
            segments.append(create_single_script_segment(segment_articles, segment_duration, segment_title))
    
    logger.info(f"Created {len(segments)} script segments")
    return segments

def create_single_script_segment(articles: List[Dict[str, Any]], duration_minutes: float, segment_title: str) -> Dict[str, Any]:
    """Create a single script segment"""
    logger.info(f"Creating script segment: {segment_title}")
    
    # Create articles text for this segment (limit articles for shorter segments)
    articles_text = ""
    for i, article in enumerate(articles[:3]):  # Max 3 articles per segment
        articles_text += f"{i+1}. **{article['title']}** (Source: {article['source']})\n"
        articles_text += f"   Summary: {article['summary'][:200]}...\n\n"
    
    # Generate script using AI
    try:
        client = Groq(api_key=GROQ_API_KEY)
        
        prompt = f"""Create a {duration_minutes:.1f}-minute podcast script segment for "{segment_title}".

Articles to cover:
{articles_text}

Requirements:
- Professional news anchor tone
- Conversational and engaging
- Include smooth transitions between stories
- Add brief intro and outro for this segment
- Target duration: {duration_minutes:.1f} minutes
- Make it sound natural and informative

Format as JSON:
{{
  "segment_title": "{segment_title}",
  "duration_minutes": {duration_minutes:.1f},
  "intro": "Brief segment introduction",
  "stories": [
    {{
      "title": "Story title",
      "source": "Source name", 
      "script_segment": "Full script text for this story"
    }}
  ],
  "outro": "Brief segment conclusion"
}}"""

        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a professional podcast script writer for a news show. Create engaging, informative scripts that sound natural when read aloud."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.7
        )
        
        # Parse the AI response
        import json
        import re
        
        ai_response = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            script_data = json.loads(json_match.group())
            
            # Ensure we have the required structure
            if 'stories' not in script_data:
                script_data['stories'] = []
                for article in articles[:3]:
                    story = {
                        "title": article['title'],
                        "source": article['source'],
                        "script_segment": f"Here's an update on {article['title']}. {article['summary']}"
                    }
                    script_data['stories'].append(story)
            
            return script_data
        else:
            raise ValueError("Could not parse AI response as JSON")
            
    except Exception as e:
        logger.error(f"Error generating script with AI: {e}")
        
        # Fallback: create basic script structure
        stories = []
        for article in articles[:3]:
            story = {
                "title": article['title'],
                "source": article['source'],
                "script_segment": f"Here's an update on {article['title']}. {article['summary']}"
            }
            stories.append(story)
        
        return {
            "segment_title": segment_title,
            "duration_minutes": duration_minutes,
            "intro": f"Welcome to {segment_title}. Let's dive into the latest updates.",
            "stories": stories,
            "outro": f"That concludes {segment_title}. Stay tuned for more news."
        }
