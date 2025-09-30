"""
Enhanced Flask Web Application for NewsCast AI
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import threading
import time

from core.episode_generator import generate_new_enhanced_episode
from utils.file_utils import get_episode_list
from utils.logging_config import get_logger
from core.config import NEWS_CATEGORIES

logger = get_logger(__name__)

app = Flask(__name__)
CORS(app)

# Global generation status
generation_status = {
    "is_generating": False,
    "progress": 0,
    "current_step": "Ready",
    "episode_number": None,
    "error": None
}

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/episodes')
def get_episodes():
    """Get list of available episodes"""
    try:
        episodes = get_episode_list()
        return jsonify({
            "success": True,
            "episodes": episodes
        })
    except Exception as e:
        logger.error(f"Error getting episodes: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/categories')
def get_categories():
    """Get available news categories"""
    return jsonify({
        "success": True,
        "categories": NEWS_CATEGORIES
    })

@app.route('/api/generate', methods=['POST'])
def generate_episode():
    """Generate a new episode"""
    global generation_status
    
    if generation_status["is_generating"]:
        return jsonify({
            "success": False,
            "error": "Episode generation already in progress"
        })
    
    try:
        data = request.json
        categories = {
            "politics": data.get('politics', ['neutral']),
            "scope": data.get('scope', ['global']),
            "topics": data.get('topics', ['technology', 'business'])
        }
        target_duration = data.get('target_duration', 35)
        custom_prompt = data.get('custom_prompt', '')
        
        # Start generation in background
        thread = threading.Thread(
            target=generate_episode_background,
            args=(categories, target_duration, custom_prompt)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "success": True,
            "message": "Episode generation started"
        })
        
    except Exception as e:
        logger.error(f"Error starting episode generation: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        })

@app.route('/api/generation-status')
def get_generation_status():
    """Get current episode generation status"""
    return jsonify(generation_status)

def generate_episode_background(categories, target_duration, custom_prompt=None):
    """Generate episode in background thread"""
    global generation_status
    
    try:
        generation_status.update({
            "is_generating": True,
            "progress": 0,
            "current_step": "Starting neural synthesis...",
            "episode_number": None,
            "error": None
        })
        
        # Step 1: Gathering news
        generation_status.update({
            "progress": 20,
            "current_step": "Scanning global information networks..."
        })
        
        # Step 2: Creating script
        generation_status.update({
            "progress": 40,
            "current_step": "Neural script generation in progress..."
        })
        
        # Step 3: Generating audio
        generation_status.update({
            "progress": 60,
            "current_step": "Synthesizing neural voice patterns..."
        })
        
        # Generate the episode
        result = generate_new_enhanced_episode(
            categories=categories,
            target_duration=target_duration,
            custom_prompt=custom_prompt if custom_prompt else None
        )
        
        if result:
            # Extract episode number from folder path
            import os
            episode_number = os.path.basename(result).split('_')[1]
            
            generation_status.update({
                "is_generating": False,
                "progress": 100,
                "current_step": f"Episode {episode_number} synthesis complete!",
                "episode_number": int(episode_number),
                "error": None
            })
        else:
            raise Exception("Episode generation returned no result")
            
    except Exception as e:
        logger.error(f"Error generating episode: {e}")
        generation_status.update({
            "is_generating": False,
            "progress": 0,
            "current_step": "Neural synthesis failed",
            "episode_number": None,
            "error": str(e)
        })

@app.route('/episodes/<path:filename>')
def serve_episode(filename):
    """Serve episode files"""
    return send_from_directory('episodes', filename)

if __name__ == '__main__':
    logger.info("Starting NewsCast AI Web Server...")
    logger.info("✓ Enhanced modular architecture loaded")
    logger.info("✓ 8-segment fast mode enabled")
    logger.info("✓ Custom prompt AI processing ready")
    app.run(host='0.0.0.0', port=5000, debug=False)
