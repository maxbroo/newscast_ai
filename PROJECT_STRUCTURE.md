# NewsCastAI Project Structure

## Directory Organization

```
NewsCastAI_Project/
├── data/                           # Data files and JSON exports
│   └── articles_20250925_121657.json
├── logs/                          # Application logs
│   └── startup.log
├── NewsCastAI-Backend/           # Main application backend
│   ├── core/                     # Core application logic
│   │   ├── config.py
│   │   └── episode_generator.py
│   ├── scrapers/                 # News scraping modules
│   │   └── news_scraper.py
│   ├── generators/               # Content generation modules
│   │   ├── audio_generator.py
│   │   └── script_generator.py
│   ├── utils/                    # Utility functions
│   │   ├── file_utils.py
│   │   └── logging_config.py
│   ├── episodes/                 # Generated episodes
│   │   ├── episode_*/           # Individual episode directories
│   │   │   ├── episode_*_complete.mp3
│   │   │   ├── episode_info.json
│   │   │   └── segment_*/       # Episode segments
│   ├── assets/                   # Static audio assets
│   │   ├── intro_music.mp3
│   │   └── outro_music.mp3
│   ├── templates/               # HTML templates
│   ├── static/                  # Static web assets
│   ├── uploads/                 # File uploads
│   ├── logs/                    # Backend-specific logs
│   ├── ffmpeg/                  # FFmpeg binaries
│   ├── archive/                 # Archived/old code
│   ├── web_app.py              # Main web application
│   ├── web_app_production.py   # Production web app
│   ├── start_enhanced.py       # Enhanced startup script
│   ├── requirements.txt        # Python dependencies
│   ├── Procfile               # Deployment configuration
│   ├── railway.toml           # Railway deployment config
│   └── README_ENHANCED.md     # Backend documentation
```

## Episode Structure Standard

Each episode follows this structure:
```
episode_N/
├── episode_N_complete.mp3      # Final combined episode
├── episode_info.json           # Episode metadata
├── segment_N/                  # Individual segments
│   ├── *.mp3                  # Segment audio files
│   └── segment_N_metadata.json # Segment metadata
```

## File Naming Conventions

- Episodes: `episode_N/` where N is the episode number
- Audio files: `episode_N_complete.mp3`, `segment_N.mp3`
- Metadata: `episode_info.json`, `segment_N_metadata.json`
- Story files: `story_N_[title].mp3`

## Development Guidelines

1. All new episodes should follow the standardized structure
2. Use the `data/` directory for storing JSON exports and data files
3. Keep logs organized in their respective `logs/` directories
4. Archive old code in the `archive/` directory
5. Use consistent naming conventions for all files
