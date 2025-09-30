# web_app.py - Flask Web Application for NewsCast AI

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
import json
import glob
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
from enhanced_main import generate_new_enhanced_episode, NewsScraper
import threading
import time

# Configure logging with file output
def setup_web_logging():
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create file handler for web app logs
    file_handler = RotatingFileHandler(
        'logs/web_app.log',
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Get logger for this module
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_web_logging()

app = Flask(__name__)
CORS(app)

# Configuration
EPISODES_DIR = "episodes"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'm4a'}

# Ensure directories exist
os.makedirs(EPISODES_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables for episode generation status
generation_status = {
    "is_generating": False,
    "progress": 0,
    "current_step": "",
    "episode_number": None,
    "error": None
}

@app.route('/')
def index():
    """Main page with episode player and controls"""
    return render_template('index.html')

@app.route('/api/episodes')
def get_episodes():
    """Get list of all available episodes"""
    try:
        episodes = []
        
        if os.path.exists(EPISODES_DIR):
            for item in os.listdir(EPISODES_DIR):
                if item.startswith("episode_"):
                    episode_path = os.path.join(EPISODES_DIR, item)
                    if os.path.isdir(episode_path):
                        # Check for complete episode
                        complete_file = os.path.join(episode_path, f"{item}_complete.mp3")
                        if os.path.exists(complete_file):
                            try:
                                episode_num = int(item.split("_")[1])
                                
                                # Load episode info
                                info_file = os.path.join(episode_path, "episode_info.json")
                                episode_info = {}
                                if os.path.exists(info_file):
                                    with open(info_file, 'r') as f:
                                        episode_info = json.load(f)
                                
                                # Get file size
                                file_size = os.path.getsize(complete_file)
                                
                                episodes.append({
                                    "episode_number": episode_num,
                                    "title": f"Episode {episode_num}",
                                    "file_path": f"/api/episodes/{episode_num}/audio",
                                    "file_size": file_size,
                                    "file_size_mb": round(file_size / (1024 * 1024), 1),
                                    "created_at": episode_info.get("created_at", ""),
                                    "articles_count": episode_info.get("articles_count", 0),
                                    "sources_used": episode_info.get("sources_used", []),
                                    "categories": episode_info.get("categories", []),
                                    "duration_minutes": episode_info.get("target_duration_minutes", 35)
                                })
                            except (ValueError, IndexError):
                                continue
        
        # Sort by episode number (newest first)
        episodes.sort(key=lambda x: x["episode_number"], reverse=True)
        
        return jsonify({
            "success": True,
            "episodes": episodes,
            "total": len(episodes)
        })
        
    except Exception as e:
        logger.error(f"Error getting episodes: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/episodes/<int:episode_number>/audio')
def stream_episode(episode_number):
    """Stream episode audio file"""
    try:
        episode_folder = os.path.join(EPISODES_DIR, f"episode_{episode_number}")
        audio_file = os.path.join(episode_folder, f"episode_{episode_number}_complete.mp3")
        
        if not os.path.exists(audio_file):
            return jsonify({"error": "Episode not found"}), 404
        
        return send_file(audio_file, as_attachment=False, mimetype='audio/mpeg')
        
    except Exception as e:
        logger.error(f"Error streaming episode {episode_number}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/episodes/<int:episode_number>/info')
def get_episode_info(episode_number):
    """Get detailed information about a specific episode"""
    try:
        episode_folder = os.path.join(EPISODES_DIR, f"episode_{episode_number}")
        
        if not os.path.exists(episode_folder):
            return jsonify({"error": "Episode not found"}), 404
        
        # Load episode info
        info_file = os.path.join(episode_folder, "episode_info.json")
        metadata_file = os.path.join(episode_folder, "episode_metadata.json")
        
        episode_info = {}
        episode_metadata = {}
        
        if os.path.exists(info_file):
            with open(info_file, 'r') as f:
                episode_info = json.load(f)
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                episode_metadata = json.load(f)
        
        return jsonify({
            "success": True,
            "episode_info": episode_info,
            "episode_metadata": episode_metadata
        })
        
    except Exception as e:
        logger.error(f"Error getting episode info for {episode_number}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate_episode():
    """Generate a new episode with custom categories"""
    global generation_status
    
    if generation_status["is_generating"]:
        return jsonify({
            "success": False,
            "error": "Episode generation already in progress"
        }), 400
    
    try:
        data = request.get_json() or {}
        
        # Extract preferences
        categories = {
            "politics": data.get("politics", ["neutral"]),
            "scope": data.get("scope", ["global"]),
            "topics": data.get("topics", [])
        }
        
        target_duration = data.get("target_duration", 35)
        
        # Start generation in background thread
        thread = threading.Thread(
            target=generate_episode_background,
            args=(categories, target_duration)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Episode generation started",
            "status": generation_status
        })
        
    except Exception as e:
        logger.error(f"Error starting episode generation: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/generation-status')
def get_generation_status():
    """Get current episode generation status"""
    return jsonify(generation_status)

def generate_episode_background(categories, target_duration):
    """Generate episode in background thread"""
    global generation_status
    
    try:
        generation_status.update({
            "is_generating": True,
            "progress": 0,
            "current_step": "Starting generation...",
            "episode_number": None,
            "error": None
        })
        
        # Step 1: Gathering news
        generation_status.update({
            "progress": 20,
            "current_step": "Gathering news from RSS feeds and web sources..."
        })
        
        scraper = NewsScraper()
        articles = scraper.gather_news_with_categories(categories, max_articles=25)
        
        if not articles:
            raise Exception("No articles found")
        
        # Step 2: Creating script
        generation_status.update({
            "progress": 40,
            "current_step": "Creating podcast script with AI..."
        })
        
        from enhanced_main import create_multiple_script_segments
        segments = create_multiple_script_segments(articles, target_duration)
        
        if not segments:
            raise Exception("Script segments generation failed")
        
        # Step 3: Generating audio
        generation_status.update({
            "progress": 60,
            "current_step": "Generating speech with AI..."
        })
        
        from enhanced_main import get_next_episode_number, create_episode_folder
        episode_number = get_next_episode_number()
        episode_folder = create_episode_folder(episode_number)
        
        generation_status.update({
            "episode_number": episode_number,
            "progress": 70,
            "current_step": "Generating audio segments..."
        })
        
        from enhanced_main import generate_multiple_segments_audio
        audio_files = generate_multiple_segments_audio(segments, episode_folder)
        
        # Step 4: Combining audio
        generation_status.update({
            "progress": 85,
            "current_step": "Combining audio segments..."
        })
        
        from enhanced_main import combine_all_segments, save_episode_metadata_multiple_segments
        combined_audio = combine_all_segments(episode_folder, episode_number)
        
        # Step 5: Saving metadata
        generation_status.update({
            "progress": 95,
            "current_step": "Saving episode metadata..."
        })
        
        # Filter out None values from audio_files
        valid_audio_files = [f for f in audio_files if f is not None]
        save_episode_metadata_multiple_segments(episode_folder, episode_number, segments, articles, valid_audio_files, combined_audio)
        
        # Complete
        generation_status.update({
            "is_generating": False,
            "progress": 100,
            "current_step": f"Episode {episode_number} completed successfully!",
            "episode_number": episode_number
        })
        
        logger.info(f"Episode {episode_number} generated successfully")
        
    except Exception as e:
        logger.error(f"Error generating episode: {e}")
        generation_status.update({
            "is_generating": False,
            "progress": 0,
            "current_step": "Generation failed",
            "error": str(e)
        })

@app.route('/api/categories')
def get_categories():
    """Get available news categories"""
    from enhanced_main import NEWS_CATEGORIES
    return jsonify({
        "success": True,
        "categories": NEWS_CATEGORIES
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "episodes_count": len([f for f in os.listdir(EPISODES_DIR) if f.startswith("episode_")]) if os.path.exists(EPISODES_DIR) else 0
    })

if __name__ == '__main__':
    print("Starting NewsCast AI Web Application...")
    print("Visit http://localhost:5000 to access the web interface")
    app.run(debug=True, host='0.0.0.0', port=5000)
