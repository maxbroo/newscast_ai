#!/usr/bin/env python3
"""
Enhanced NewsCast AI Server Startup Script
Uses the new modular architecture with 8-segment fast mode
"""

import os
import sys
import subprocess
import importlib.util
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'flask', 'flask_cors', 'feedparser', 'requests', 'groq', 'openai',
        'pydub', 'beautifulsoup4', 'tweepy', 'lxml'
    ]
    
    missing_packages = []
    
    print("Checking dependencies...")
    for package in required_packages:
        try:
            if package == 'flask_cors':
                import flask_cors
            elif package == 'beautifulsoup4':
                import bs4
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        print("✓ Dependencies installed successfully")
    
    print("✓ Dependencies check passed")

def check_directories():
    """Ensure required directories exist"""
    directories = ['episodes', 'uploads', 'templates', 'static', 'logs']
    
    print("\nSetting up directories...")
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✓ Created {directory}/")
        else:
            print(f"✓ {directory}/")
    
    print("✓ Directories check passed")

def check_ffmpeg():
    """Check if ffmpeg is available"""
    print("\nChecking ffmpeg...")
    
    # Try to find ffmpeg
    ffmpeg_paths = [
        'ffmpeg',  # In PATH
        'ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe',  # Local Windows
        'ffmpeg/bin/ffmpeg.exe',  # Alternative local
        'ffmpeg.exe'  # Current directory
    ]
    
    for path in ffmpeg_paths:
        try:
            result = subprocess.run([path, '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"✓ ffmpeg found at: {path}")
                print("✓ FFmpeg check passed")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            continue
    
    print("✗ ffmpeg not found")
    print("Please install ffmpeg or place it in the ffmpeg/ directory")
    return False

def check_api_keys():
    """Check if API keys are configured"""
    print("\nChecking API keys...")
    
    try:
        from core.config import GROQ_API_KEY, OPENAI_API_KEY
        
        if GROQ_API_KEY and not GROQ_API_KEY.startswith('your_'):
            print("✓ GROQ API key configured")
        else:
            print("✗ GROQ API key not configured")
            return False
        
        if OPENAI_API_KEY and not OPENAI_API_KEY.startswith('your_'):
            print("✓ OpenAI API key configured")
        else:
            print("✗ OpenAI API key not configured")
            return False
        
        print("✓ API Keys check passed")
        return True
        
    except ImportError as e:
        print(f"✗ Error importing config: {e}")
        return False

def main():
    """Main startup function"""
    print("=" * 60)
    print("🚀 NewsCast AI - Enhanced Neural News Network")
    print("=" * 60)
    print(f"Startup Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project Root: {project_root}")
    print()
    
    # Run all checks
    try:
        check_dependencies()
        check_directories()
        
        if not check_ffmpeg():
            print("\n⚠️  Warning: ffmpeg not found. Audio generation may fail.")
            input("Press Enter to continue anyway, or Ctrl+C to exit...")
        
        if not check_api_keys():
            print("\n❌ API keys not configured. Please update core/config.py")
            sys.exit(1)
        
        print("\n" + "=" * 60)
        print("All checks passed! Starting enhanced web server...")
        print("=" * 60)
        print()
        
        # Import and start the enhanced web app
        from web_app import app, logger
        
        logger.info("🧠 Enhanced NewsCast AI Web Server Starting...")
        logger.info("✓ Modular architecture loaded")
        logger.info("✓ 8-segment fast mode enabled")
        logger.info("✓ Custom AI prompt processing ready") 
        logger.info("✓ 12 news categories available")
        logger.info("✓ Unicode handling fixed")
        
        print("🌐 Server Features:")
        print("   • Neural-themed UI with particle animations")
        print("   • 8-segment fast mode (3-5 min generation)")
        print("   • Custom AI prompt processing")
        print("   • 12+ news categories")
        print("   • Mobile-responsive design")
        print()
        print("🔗 Access your Neural News Network at:")
        print("   • http://localhost:5000")
        print("   • http://127.0.0.1:5000")
        print()
        print("✨ Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Start the Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
