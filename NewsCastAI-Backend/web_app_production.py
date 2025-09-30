"""
Production Flask Web Application for NewsCast AI with Scheduling
Optimized for Railway deployment and mobile access
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import threading
import time
import schedule
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

from core.episode_generator import generate_new_enhanced_episode
from utils.file_utils import get_episode_list
from utils.logging_config import get_logger
from core.config import NEWS_CATEGORIES

# Load environment variables
load_dotenv()

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

# User preferences storage (in production, store in file or database)
PREFERENCES_FILE = "user_preferences.json"

def load_preferences():
    """Load user preferences from file"""
    default_preferences = {
        "morning_generation": {
            "enabled": False,
            "time": "07:00",  # 7 AM
            "politics": ["neutral"],
            "scope": ["global"],
            "topics": ["technology", "business"],
            "duration": 35,
            "custom_prompt": ""
        }
    }
    
    try:
        if os.path.exists(PREFERENCES_FILE):
            with open(PREFERENCES_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Error loading preferences: {e}")
    
    return default_preferences

def save_preferences(preferences):
    """Save user preferences to file"""
    try:
        with open(PREFERENCES_FILE, 'w') as f:
            json.dump(preferences, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Error saving preferences: {e}")
        return False

# Load initial preferences
user_preferences = load_preferences()

@app.route('/')
def index():
    """Main page"""
    return render_template('index_mobile.html')

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

@app.route('/api/preferences', methods=['GET', 'POST'])
def handle_preferences():
    """Get or update user preferences"""
    global user_preferences
    
    if request.method == 'GET':
        return jsonify({
            "success": True,
            "preferences": user_preferences
        })
    
    elif request.method == 'POST':
        try:
            data = request.json
            user_preferences.update(data)
            
            # Save to file
            if save_preferences(user_preferences):
                # Restart scheduler if morning generation settings changed
                if 'morning_generation' in data:
                    restart_scheduler()
                
                return jsonify({
                    "success": True,
                    "message": "Preferences updated successfully"
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "Failed to save preferences"
                })
        except Exception as e:
            logger.error(f"Error updating preferences: {e}")
            return jsonify({
                "success": False,
                "error": str(e)
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

def generate_morning_episode():
    """Generate morning episode based on user preferences"""
    global generation_status, user_preferences
    
    if generation_status["is_generating"]:
        logger.warning("Morning generation skipped - already generating")
        return
    
    prefs = user_preferences["morning_generation"]
    if not prefs["enabled"]:
        logger.info("Morning generation disabled")
        return
    
    logger.info("Starting scheduled morning episode generation...")
    
    categories = {
        "politics": prefs["politics"],
        "scope": prefs["scope"],
        "topics": prefs["topics"]
    }
    
    custom_prompt = prefs.get("custom_prompt", "")
    
    # Start generation in background
    thread = threading.Thread(
        target=generate_episode_background,
        args=(categories, prefs["duration"], custom_prompt)
    )
    thread.daemon = True
    thread.start()

def start_scheduler():
    """Start the background scheduler"""
    if user_preferences["morning_generation"]["enabled"]:
        time_str = user_preferences["morning_generation"]["time"]
        schedule.every().day.at(time_str).do(generate_morning_episode)
        logger.info(f"Morning generation scheduled for {time_str}")
    
    # Run scheduler in background thread
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

def restart_scheduler():
    """Restart the scheduler with new settings"""
    schedule.clear()
    start_scheduler()

@app.route('/episodes/<path:filename>')
def serve_episode(filename):
    """Serve episode files"""
    return send_from_directory('episodes', filename)

@app.route('/health')
def health_check():
    """Health check endpoint for Railway"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/test-keys')
def test_api_keys():
    """Test endpoint to check if API keys are working"""
    from core.config import GROQ_API_KEY, OPENAI_API_KEY
    
    result = {
        "groq_key_set": GROQ_API_KEY != "your_groq_api_key_here",
        "groq_key_length": len(GROQ_API_KEY) if GROQ_API_KEY else 0,
        "groq_key_preview": f"{GROQ_API_KEY[:10]}...{GROQ_API_KEY[-4:]}" if GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here" else "Not set",
        "openai_key_set": OPENAI_API_KEY != "your_openai_api_key_here", 
        "openai_key_length": len(OPENAI_API_KEY) if OPENAI_API_KEY else 0,
        "openai_key_preview": f"{OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]}" if OPENAI_API_KEY and OPENAI_API_KEY != "your_openai_api_key_here" else "Not set"
    }
    
    return jsonify(result)

if __name__ == '__main__':
    logger.info("Starting NewsCast AI Production Server...")
    logger.info("✓ Enhanced modular architecture loaded")
    logger.info("✓ 8-segment fast mode enabled")
    logger.info("✓ Custom prompt AI processing ready")
    logger.info("✓ Morning generation scheduling enabled")
    logger.info("✓ Mobile-optimized interface ready")
    
    # Start scheduler
    start_scheduler()
    
    # Get port from environment (Railway sets this automatically)
    port = int(os.environ.get('PORT', 5000))
    
    print("🌐 Production Server Features:")
    print("   • Mobile-optimized neural UI")
    print("   • 8-segment fast mode (3-5 min generation)")
    print("   • Custom AI prompt processing")
    print("   • 12+ news categories")
    print("   • iPhone-friendly responsive design")
    print("   • Morning generation scheduling")
    print()
    print(f"🔗 Access your Neural News Network at:")
    print(f"   • http://localhost:{port}")
    print(f"   • Railway will provide public URL")
    print()
    print("✨ Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the Flask app
    app.run(host='0.0.0.0', port=port, debug=False)
