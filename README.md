# NewsCastAI Project

An AI-powered news podcast generation system that scrapes news articles and creates audio episodes with multiple segments.

## Project Structure

```
NewsCastAI_Project/
├── data/                          # Data files and exports
├── logs/                         # Application logs
├── NewsCastAI-Backend/          # Main application
│   ├── core/                    # Core application logic
│   ├── scrapers/                # News scraping modules
│   ├── generators/              # Content generation
│   ├── utils/                   # Utility functions
│   ├── episodes/                # Generated episodes
│   │   └── episode_*/          # Individual episodes
│   │       ├── episode_*_complete.mp3
│   │       ├── episode_info.json
│   │       └── segments/       # Episode segments
│   ├── assets/                  # Static audio assets
│   ├── templates/              # HTML templates
│   ├── static/                 # Web assets
│   ├── ffmpeg/                 # Audio processing tools
│   └── archive/                # Archived code
├── PROJECT_STRUCTURE.md        # Detailed structure docs
└── README.md                   # This file
```

## Quick Start

1. Navigate to the backend directory:
   ```bash
   cd NewsCastAI-Backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python web_app.py
   ```

## Features

- **News Scraping**: Automated news article collection
- **AI Content Generation**: Script and audio generation
- **Episode Management**: Organized episode structure
- **Web Interface**: User-friendly web application
- **Audio Processing**: Complete audio pipeline with FFmpeg

## Episode Structure

Each episode contains:
- Complete episode audio file
- Episode metadata (JSON)
- Individual segments in organized directories
- Consistent naming conventions

## Development

- Main application: `NewsCastAI-Backend/web_app.py`
- Production version: `NewsCastAI-Backend/web_app_production.py`
- Configuration: `NewsCastAI-Backend/core/config.py`

## Deployment

The project includes configuration for Railway deployment:
- `Procfile` - Process configuration
- `railway.toml` - Railway-specific settings
- `runtime.txt` - Python version specification

For detailed structure information, see `PROJECT_STRUCTURE.md`.
