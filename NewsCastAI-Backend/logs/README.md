# NewsCast AI Logging System

This directory contains log files for the NewsCast AI application.

## Log Files

- **`newscast_ai.log`** - Main application logs from enhanced_main.py
- **`web_app.log`** - Web application logs from Flask server
- **`startup.log`** - Server startup and dependency check logs
- **`test.log`** - Test script execution logs

## Log Rotation

All log files use rotating file handlers:
- Main logs: 10MB max size, 5 backup files
- Web app logs: 5MB max size, 3 backup files  
- Startup/Test logs: 2MB max size, 2 backup files

## Viewing Logs

Use the included `view_logs.py` script:

```bash
# List all log files
python view_logs.py --list

# View last 50 lines of main log
python view_logs.py

# View specific log file
python view_logs.py --file web_app.log

# View last 100 lines
python view_logs.py --lines 100

# Follow log file (like tail -f)
python view_logs.py --follow

# Follow specific log file
python view_logs.py --file startup.log --follow
```

## Log Format

All logs use the format:
```
YYYY-MM-DD HH:MM:SS - module_name - LEVEL - message
```

Example:
```
2025-09-24 10:30:15 - enhanced_main - INFO - Starting episode generation
2025-09-24 10:30:16 - web_app - ERROR - Failed to load episode metadata
```

## Log Levels

- **INFO** - General information about application flow
- **WARNING** - Potential issues that don't stop execution
- **ERROR** - Errors that may affect functionality
- **DEBUG** - Detailed diagnostic information (not used by default)

## Maintenance

Log files are automatically rotated when they reach their size limits. Old log files are kept with numbered extensions (.1, .2, etc.) and automatically cleaned up when the backup count is exceeded.
