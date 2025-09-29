"""
File utility functions for NewsCast AI
"""

import os
import glob
import shutil
import json
from datetime import datetime
from typing import List, Dict, Any

from utils.logging_config import get_logger

logger = get_logger(__name__)

def find_ffmpeg():
    """Find ffmpeg executable in the system"""
    # Check if ffmpeg is in PATH
    if shutil.which('ffmpeg'):
        return 'ffmpeg'
    
    # Check local ffmpeg directory
    local_ffmpeg_paths = [
        'ffmpeg/ffmpeg-master-latest-win64-gpl/bin/ffmpeg.exe',
        'ffmpeg/bin/ffmpeg.exe',
        'ffmpeg.exe'
    ]
    
    for path in local_ffmpeg_paths:
        if os.path.exists(path):
            return path
    
    logger.error("ffmpeg not found in PATH or local directories")
    return None

def get_next_episode_number() -> int:
    """Get the next episode number by checking existing episodes folder"""
    episodes_dir = "episodes"
    if not os.path.exists(episodes_dir):
        return 1
    
    episode_folders = [f for f in os.listdir(episodes_dir) if f.startswith("episode_")]
    if not episode_folders:
        return 1
    
    # Extract episode numbers and find the highest
    episode_numbers = []
    for folder in episode_folders:
        try:
            num = int(folder.split("_")[1])
            episode_numbers.append(num)
        except (ValueError, IndexError):
            continue
    
    return max(episode_numbers) + 1 if episode_numbers else 1

def create_episode_folder(episode_number: int) -> str:
    """Create and return the episode folder path"""
    episode_folder = os.path.join("episodes", f"episode_{episode_number}")
    os.makedirs(episode_folder, exist_ok=True)
    return episode_folder

def save_episode_metadata(episode_folder: str, episode_number: int, segments: List[Dict[str, Any]], 
                         articles: List[Dict[str, Any]], audio_files: List[str], combined_audio: str):
    """Save episode metadata for multiple segments approach"""
    # Calculate total target duration
    total_duration = sum(segment.get('duration_minutes', 4.5) for segment in segments)
    
    # Save segments metadata
    segments_metadata = {
        "episode_number": episode_number,
        "created_at": datetime.now().isoformat(),
        "segments": segments,
        "articles_count": len(articles),
        "audio_files": [os.path.basename(f) for f in audio_files if f],
        "combined_audio": os.path.basename(combined_audio) if combined_audio else None,
        "sources_used": list(set([article["source"] for article in articles])),
        "categories": list(set([article.get("category", "general") for article in articles])),
        "target_duration_minutes": int(total_duration),
        "segments_count": len(segments)
    }
    
    episode_info_filename = os.path.join(episode_folder, "episode_info.json")
    with open(episode_info_filename, 'w', encoding='utf-8') as f:
        json.dump(segments_metadata, f, indent=2, ensure_ascii=False)
    
    # Also save individual segment metadata
    for i, segment in enumerate(segments):
        segment_metadata_file = os.path.join(episode_folder, f"segment_{i+1}_metadata.json")
        with open(segment_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(segment, f, indent=2, ensure_ascii=False)

def get_episode_list() -> List[Dict[str, Any]]:
    """Get list of all available episodes with metadata"""
    episodes = []
    episodes_dir = "episodes"
    
    if not os.path.exists(episodes_dir):
        return episodes
    
    episode_folders = [f for f in os.listdir(episodes_dir) if f.startswith("episode_")]
    episode_folders.sort(key=lambda x: int(x.split("_")[1]), reverse=True)  # Newest first
    
    for folder in episode_folders:
        episode_path = os.path.join(episodes_dir, folder)
        episode_info_file = os.path.join(episode_path, "episode_info.json")
        
        if os.path.exists(episode_info_file):
            try:
                with open(episode_info_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                # Find the complete episode file
                complete_file = None
                for file in os.listdir(episode_path):
                    if file.endswith("_complete.mp3"):
                        complete_file = file
                        break
                
                if complete_file:
                    file_path = os.path.join(episode_path, complete_file)
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    
                    episode_data = {
                        "episode_number": metadata.get("episode_number"),
                        "title": f"Episode {metadata.get('episode_number')} - AI News Roundup",
                        "created_at": metadata.get("created_at"),
                        "duration_minutes": metadata.get("target_duration_minutes", 35),
                        "articles_count": metadata.get("articles_count", 0),
                        "segments_count": metadata.get("segments_count", 8),
                        "categories": metadata.get("categories", []),
                        "sources_used": metadata.get("sources_used", []),
                        "file_path": f"/episodes/{folder}/{complete_file}",
                        "file_size_mb": f"{file_size / (1024*1024):.1f}"
                    }
                    episodes.append(episode_data)
                    
            except Exception as e:
                logger.error(f"Error reading episode metadata for {folder}: {e}")
    
    return episodes

def cleanup_temp_files(episode_folder: str):
    """Clean up temporary files after episode generation"""
    try:
        # Remove file list files
        for file in glob.glob(os.path.join(episode_folder, "*_list.txt")):
            os.remove(file)
        
        # Optionally remove individual segment files to save space
        # (Keep them for now for debugging purposes)
        
        logger.info(f"Cleaned up temporary files in {episode_folder}")
    except Exception as e:
        logger.error(f"Error cleaning up temp files: {e}")
