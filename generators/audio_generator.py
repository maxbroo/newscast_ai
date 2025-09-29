"""
Audio generation functionality for NewsCast AI
"""

import os
import subprocess
import re
from typing import List, Dict, Any
from openai import OpenAI

from core.config import OPENAI_API_KEY, AUDIO_SETTINGS
from utils.logging_config import get_logger
from utils.file_utils import find_ffmpeg

logger = get_logger(__name__)

def generate_multiple_segments_audio(segments: List[Dict[str, Any]], episode_folder: str) -> List[str]:
    """Generate audio for multiple script segments and combine them"""
    logger.info(f"Generating audio for {len(segments)} script segments...")
    
    all_audio_files = []
    successful_segments = 0
    
    for i, segment in enumerate(segments):
        logger.info(f"Processing segment {i+1}/{len(segments)}: {segment.get('segment_title', 'Unknown')}")
        
        try:
            # Create segment folder
            segment_folder = os.path.join(episode_folder, f"segment_{i+1}")
            os.makedirs(segment_folder, exist_ok=True)
            
            # Generate audio for this segment
            segment_audio_files = generate_segment_audio(segment, segment_folder, i+1)
            if segment_audio_files:
                all_audio_files.extend([f for f in segment_audio_files if f])
                
                # Combine this segment into a single file
                segment_combined = combine_segment_audio(segment_folder, i+1)
                if segment_combined and os.path.exists(segment_combined) and os.path.getsize(segment_combined) > 0:
                    all_audio_files.append(segment_combined)
                    successful_segments += 1
                    logger.info(f"[OK] Segment {i+1} completed successfully")
                else:
                    logger.warning(f"[FAIL] Segment {i+1} combination failed")
            else:
                logger.warning(f"[FAIL] Segment {i+1} audio generation failed")
                
        except Exception as e:
            logger.error(f"[ERROR] Error processing segment {i+1}: {e}")
            continue
    
    logger.info(f"Generated audio for {successful_segments}/{len(segments)} segments successfully")
    return [f for f in all_audio_files if f]  # Remove None values

def generate_segment_audio(segment: Dict[str, Any], segment_folder: str, segment_number: int) -> List[str]:
    """Generate audio files for a single segment"""
    logger.info(f"Generating audio for segment {segment_number}...")
    
    audio_files = []
    
    # Generate intro
    intro_text = segment.get("intro", "")
    if intro_text:
        result = generate_audio_segment(f"segment_{segment_number}_intro", intro_text, segment_folder)
        if result:
            audio_files.append(result)
    
    # Generate stories
    stories = segment.get("stories", [])
    for i, story in enumerate(stories):
        script_segment = story.get('script_segment', '')
        if isinstance(script_segment, dict):
            if 'script' in script_segment:
                script_segment = script_segment['script']
            elif 'text' in script_segment:
                script_segment = script_segment['text']
            else:
                script_segment = str(script_segment)
        
        story_text = f"From {story['source']}: {story['title']}. {script_segment}"
        # Create a safe filename by removing special characters and limiting length
        safe_title = re.sub(r'[<>:"/\\|?*\u014d\u2713\u2717]', '', story['title'])[:30]
        safe_title = safe_title.replace(' ', '_')
        # Remove any remaining Unicode characters that might cause issues
        safe_title = safe_title.encode('ascii', 'ignore').decode('ascii')
        result = generate_audio_segment(f"segment_{segment_number}_story_{i+1}_{safe_title}", story_text, segment_folder)
        if result:
            audio_files.append(result)
    
    # Generate outro
    outro_text = segment.get("outro", "")
    if outro_text:
        result = generate_audio_segment(f"segment_{segment_number}_outro", outro_text, segment_folder)
        if result:
            audio_files.append(result)
    
    return audio_files

def generate_audio_segment(name: str, text: str, episode_folder: str) -> str:
    """Generate audio for a single text segment using OpenAI TTS"""
    try:
        logger.info(f"Generating TTS for {name}: {text[:100]}...")
        
        # Debug API key
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
            logger.error(f"OpenAI API key not set properly. Current value: {OPENAI_API_KEY[:10] if OPENAI_API_KEY else 'None'}...")
            return None
        
        # Log API key info for debugging (first 10 chars only)
        logger.debug(f"Using OpenAI API key: {OPENAI_API_KEY[:10]}...{OPENAI_API_KEY[-4:]} (length: {len(OPENAI_API_KEY)})")
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        
        speech_file = os.path.join(episode_folder, f"{name}.mp3")
        
        with open(speech_file, "wb") as f:
            f.write(response.content)
        
        logger.info(f"Saved {name} audio to {speech_file}")
        return speech_file
        
    except Exception as e:
        logger.error(f"Error generating audio for {name}: {e}")
        # Log more details about the API key for debugging
        logger.error(f"API key details - Length: {len(OPENAI_API_KEY) if OPENAI_API_KEY else 0}, Starts with: {OPENAI_API_KEY[:20] if OPENAI_API_KEY else 'None'}...")
        return None

def combine_segment_audio(segment_folder: str, segment_number: int) -> str:
    """Combine all audio files in a segment into one file"""
    logger.info(f"Combining audio for segment {segment_number}...")
    
    audio_files = []
    for file in os.listdir(segment_folder):
        if file.endswith('.mp3') and not file.endswith('_complete.mp3'):
            file_path = os.path.join(segment_folder, file)
            # Check if file has content (not 0 bytes)
            if os.path.getsize(file_path) > 0:
                audio_files.append(file_path)
                logger.info(f"Added valid audio file: {file}")
            else:
                logger.warning(f"Skipping empty audio file: {file}")
    
    if not audio_files:
        logger.error(f"No valid audio files found in segment {segment_number}")
        return None
    
    # Sort files properly
    def sort_key(filepath):
        filename = os.path.basename(filepath)
        if 'intro' in filename:
            return (0, filename)
        elif 'outro' in filename:
            return (99, filename)
        elif 'story' in filename:
            return (10, filename)
        else:
            return (20, filename)
    
    audio_files.sort(key=sort_key)
    
    # Create file list for ffmpeg
    file_list_path = os.path.join(segment_folder, "file_list.txt")
    with open(file_list_path, 'w', encoding='utf-8') as f:
        for audio_file in audio_files:
            relative_path = os.path.relpath(audio_file, segment_folder)
            relative_path = relative_path.replace('\\', '/')
            # Ensure ASCII-safe file paths
            relative_path = relative_path.encode('ascii', 'ignore').decode('ascii')
            f.write(f"file '{relative_path}'\n")
    
    output_file = os.path.join(segment_folder, f"segment_{segment_number}_complete.mp3")
    
    # Find ffmpeg
    ffmpeg_cmd = find_ffmpeg()
    if not ffmpeg_cmd:
        logger.error("ffmpeg not found")
        return None
    
    # Build ffmpeg command with faster settings
    settings = AUDIO_SETTINGS["fast_mode"]
    cmd = [
        ffmpeg_cmd,
        "-f", "concat",
        "-safe", "0",
        "-i", file_list_path,
        "-c:a", "libmp3lame",
        "-b:a", settings["bitrate"],
        "-ar", settings["sample_rate"], 
        "-ac", settings["channels"],
        "-q:a", settings["quality"],
        "-y",
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"Segment {segment_number} combined successfully")
            os.remove(file_list_path)
            return output_file
        else:
            logger.error(f"Error combining segment {segment_number}: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error combining segment {segment_number}: {e}")
        return None

def combine_all_segments(episode_folder: str, episode_number: int) -> str:
    """Combine all segment audio files into the final episode"""
    logger.info(f"Combining all segments for Episode {episode_number}...")
    
    # Find all segment complete files
    segment_files = []
    for item in os.listdir(episode_folder):
        if item.startswith("segment_") and item.endswith("_complete.mp3"):
            file_path = os.path.join(episode_folder, item)
            if os.path.getsize(file_path) > 0:
                segment_files.append(file_path)
                logger.info(f"Found valid segment file: {item}")
            else:
                logger.warning(f"Skipping empty segment file: {item}")
    
    if not segment_files:
        logger.info("No segment complete files found, trying to combine individual segments...")
        # Try to find individual segment folders and combine them
        segment_folders = [f for f in os.listdir(episode_folder) if f.startswith("segment_") and os.path.isdir(os.path.join(episode_folder, f))]
        logger.info(f"Found segment folders: {segment_folders}")
        
        for folder in sorted(segment_folders):
            segment_folder_path = os.path.join(episode_folder, folder)
            segment_num = int(folder.split('_')[1])
            segment_combined = combine_segment_audio(segment_folder_path, segment_num)
            if segment_combined and os.path.getsize(segment_combined) > 0:
                segment_files.append(segment_combined)
                logger.info(f"Successfully combined segment {segment_num}")
            else:
                logger.warning(f"Failed to combine segment {segment_num}")
        
        if not segment_files:
            logger.error("No valid segment files found after trying to combine individual segments")
            return None
    
    # Sort segments by number
    def sort_key(filepath):
        filename = os.path.basename(filepath)
        # Extract segment number from filename like "segment_1_complete.mp3"
        try:
            segment_num = int(filename.split('_')[1])
            return segment_num
        except (ValueError, IndexError):
            return 0
    
    segment_files.sort(key=sort_key)
    
    # Create file list for ffmpeg
    file_list_path = os.path.join(episode_folder, "all_segments_list.txt")
    with open(file_list_path, 'w', encoding='utf-8') as f:
        for segment_file in segment_files:
            relative_path = os.path.relpath(segment_file, episode_folder)
            relative_path = relative_path.replace('\\', '/')
            # Ensure ASCII-safe file paths
            relative_path = relative_path.encode('ascii', 'ignore').decode('ascii')
            f.write(f"file '{relative_path}'\n")
    
    output_file = os.path.join(episode_folder, f"episode_{episode_number}_complete.mp3")
    
    # Find ffmpeg
    ffmpeg_cmd = find_ffmpeg()
    if not ffmpeg_cmd:
        logger.error("ffmpeg not found")
        return None
    
    # Build ffmpeg command with faster settings
    settings = AUDIO_SETTINGS["fast_mode"]
    cmd = [
        ffmpeg_cmd,
        "-f", "concat",
        "-safe", "0",
        "-i", file_list_path,
        "-c:a", "libmp3lame",
        "-b:a", settings["bitrate"],
        "-ar", settings["sample_rate"],
        "-ac", settings["channels"],
        "-q:a", settings["quality"],
        "-y",
        output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"All segments combined successfully: {output_file}")
            os.remove(file_list_path)
            return output_file
        else:
            logger.error(f"Error combining all segments: {result.stderr}")
            return None
    except Exception as e:
        logger.error(f"Error combining all segments: {e}")
        return None
