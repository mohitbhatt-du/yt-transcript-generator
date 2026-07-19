# import logging
# import random
# import threading
# import time

# from youtube_transcript_api import YouTubeTranscriptApi


# # ==========================================
# # Configuration
# # ==========================================

# MAX_RETRIES = 3

# CACHE_TTL = 60 * 60 * 24      # 24 Hours

# BASE_BACKOFF = 1.0

# LANGUAGES = [

#     "hi",
#     "en",
#     "en-US",
#     "hi-IN"

# ]


# # ==========================================
# # Logging
# # ==========================================

# logging.basicConfig(

#     level=logging.INFO,

#     format="%(asctime)s | %(levelname)s | %(message)s"

# )

# logger = logging.getLogger(__name__)


# # ==========================================
# # In-Memory Cache
# # ==========================================

# cache = {}

# cache_lock = threading.Lock()


# # cache format
# #
# # cache = {
# #
# #     video_id:{
# #
# #         "timestamp":123456,
# #
# #         "data":{...}
# #
# #     }
# #
# # }


# # ==========================================
# # Cache Helpers
# # ==========================================

# def get_cached(video_id):

#     with cache_lock:

#         item = cache.get(video_id)

#         if not item:

#             return None

#         age = time.time() - item["timestamp"]

#         if age > CACHE_TTL:

#             del cache[video_id]

#             return None

#         logger.info(f"Cache HIT : {video_id}")

#         cached_data = item["data"].copy()

#         cached_data["cached"] = True

#         return cached_data


# def save_cache(video_id, data):

#     with cache_lock:

#         cache[video_id] = {

#             "timestamp": time.time(),

#             "data": data

#         }

#         logger.info(f"Cached : {video_id}")


# # ==========================================
# # Cache Cleanup
# # ==========================================

# def cleanup_cache():

#     now = time.time()

#     expired = []

#     with cache_lock:

#         for key, value in cache.items():

#             age = now - value["timestamp"]

#             if age > CACHE_TTL:

#                 expired.append(key)

#         for key in expired:

#             del cache[key]

#     if expired:

#         logger.info(

#             f"Removed {len(expired)} expired cache entries."

#         )


# # ==========================================
# # Retry Delay
# # ==========================================

# def retry_delay(attempt):

#     delay = BASE_BACKOFF * (2 ** attempt)

#     jitter = random.uniform(0.0, 0.5)

#     return delay + jitter


# # ==========================================
# # Fetch With Retry
# # ==========================================

# def fetch_with_retry(video_id):

#     last_error = RuntimeError("Transcript fetch failed.")

#     for attempt in range(MAX_RETRIES):

#         try:

#             logger.info(
#                 f"Fetching transcript ({attempt+1}/{MAX_RETRIES}) : {video_id}"
#             )

#             return YouTubeTranscriptApi().fetch(
#                 video_id,
#                 languages=LANGUAGES
#             )

#         except Exception as e:

#             last_error = e

#             wait = retry_delay(attempt)

#             logger.warning(
#                 f"Attempt {attempt+1} failed. Retrying in {wait:.2f} sec..."
#             )

#             time.sleep(wait)

#     raise last_error

# # ==========================================
# # Get Transcript
# # ==========================================

# def get_transcript(video_id):

#     cleanup_cache()

#     cached = get_cached(video_id)

#     if cached:

#         return cached

#     try:

#         transcript_data = fetch_with_retry(video_id)

#         segments = []

#         raw_text = []

#         total_words = 0

#         total_characters = 0

#         total_duration = 0.0

#         for item in transcript_data:

#             text = item.text.strip()

#             raw_text.append(text)

#             total_words += len(text.split())

#             total_characters += len(text)

#             total_duration = max(
#                 total_duration,
#                 item.start + item.duration
#             )

#             segments.append({

#                 "text": text,

#                 "start": round(item.start, 2),

#                 "duration": round(item.duration, 2)

#             })

#         result = {

#             "success": True,

#             "video_id": video_id,

#             "language": transcript_data.language_code,

#             "segment_count": len(segments),

#             "word_count": total_words,

#             "character_count": total_characters,

#             "duration": round(total_duration, 2),

#             "cached": False,

#             "raw_text": " ".join(raw_text),

#             "segments": segments

#         }

#         save_cache(video_id, result)

#         logger.info(

#             f"Transcript fetched successfully : {video_id}"

#         )

#         return result

#     except Exception as e:

#         logger.exception(

#             f"Failed to fetch transcript : {video_id}"

#         )

#         return {

#             "success": False,


import logging
import random
import threading
import time
import re
import requests

# ==========================================
# Configuration
# ==========================================
MAX_RETRIES = 3
CACHE_TTL = 60 * 60 * 24      # 24 Hours
BASE_BACKOFF = 1.0
LANGUAGES = ["hi", "en", "en-US", "hi-IN"]

# Public Piped API mirrors that proxy requests to bypass Render IP blocks
PIPED_INSTANCES = [
    "https://api.piped.video",
    "https://pipedapi.kavin.rocks",
    "https://pipedapi.moomoo.me",
    "https://pipedapi.okko.dev"
]

# ==========================================
# Logging & Cache
# ==========================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

cache = {}
cache_lock = threading.Lock()

# ==========================================
# Compatibility Wrappers for your existing loop
# ==========================================
class MockTranscriptItem:
    def __init__(self, text, start, duration):
        self.text = text
        self.start = start
        self.duration = duration

class MockTranscriptResponse(list):
    def __init__(self, items, language_code="en"):
        super().__init__(items)
        self.language_code = language_code

# ==========================================
# VTT Transcript Parser
# ==========================================
def parse_time_to_seconds(time_str: str) -> float:
    """Converts VTT timestamp (HH:MM:SS.mmm or MM:SS.mmm) to total seconds."""
    parts = time_str.split(':')
    if len(parts) == 2:
        minutes, seconds = float(parts[0]), float(parts[1])
        return (minutes * 60) + seconds
    elif len(parts) == 3:
        hours, minutes, seconds = float(parts[0]), float(parts[1]), float(parts[2])
        return (hours * 3600) + (minutes * 60) + seconds
    return 0.0

def parse_vtt_to_items(vtt_text: str) -> list:
    """Parses standard WebVTT text data into compatibility object segments."""
    items = []
    # Split text blocks by double-newlines typical of VTT structure
    blocks = re.split(r'\n\s*\n', vtt_text.strip())
    
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
            
        # Match timestamp lines (e.g., 00:12.340 --> 00:15.120 or 01:02:03.400 --> ...)
        time_match = re.match(r'(\d[\d:.]*)\s*-->\s*(\d[\d:.]*)', lines[0])
        
        if time_match and len(lines) > 1:
            start_sec = parse_time_to_seconds(time_match.group(1))
            end_sec = parse_time_to_seconds(time_match.group(2))
            duration = max(0.0, end_sec - start_sec)
            
            # Combine any text lines belonging to this timestamp segment
            text_content = " ".join(lines[1:])
            items.append(MockTranscriptItem(text_content, start_sec, duration))
        elif len(lines) > 2:
            # Handle instances where line 0 is a counter index instead of the timestamp
            time_match_idx = re.match(r'(\d[\d:.]*)\s*-->\s*(\d[\d:.]*)', lines[1])
            if time_match_idx:
                start_sec = parse_time_to_seconds(time_match_idx.group(1))
                end_sec = parse_time_to_seconds(time_match_idx.group(2))
                duration = max(0.0, end_sec - start_sec)
                text_content = " ".join(lines[2:])
                items.append(MockTranscriptItem(text_content, start_sec, duration))
                
    return items

# ==========================================
# Cache Helpers
# ==========================================
def get_cached(video_id):
    with cache_lock:
        item = cache.get(video_id)
        if not item:
            return None
        age = time.time() - item["timestamp"]
        if age > CACHE_TTL:
            del cache[video_id]
            return None
        logger.info(f"Cache HIT : {video_id}")
        cached_data = item["data"].copy()
        cached_data["cached"] = True
        return cached_data

def save_cache(video_id, data):
    with cache_lock:
        cache[video_id] = {
            "timestamp": time.time(),
            "data": data
        }
        logger.info(f"Cached : {video_id}")

def cleanup_cache():
    now = time.time()
    expired = []
    with cache_lock:
        for key, value in cache.items():
            age = now - value["timestamp"]
            if age > CACHE_TTL:
                expired.append(key)
        for key in expired:
            del cache[key]
    if expired:
        logger.info(f"Removed {len(expired)} expired cache entries.")

# ==========================================
# Retry Delay
# ==========================================
def retry_delay(attempt):
    delay = BASE_BACKOFF * (2 ** attempt)
    jitter = random.uniform(0.0, 0.5)
    return delay + jitter

# ==========================================
# Fetch With Retry (Bypassing Method)
# ==========================================
def fetch_with_retry(video_id):
    last_error = RuntimeError("Transcript proxy fetch failed.")
    
    for attempt in range(MAX_RETRIES):
        # Select a proxy instance node dynamically based on retry index or random choice
        instance = PIPED_INSTANCES[attempt % len(PIPED_INSTANCES)]
        api_url = f"{instance}/streams/{video_id}"
        
        try:
            logger.info(f"Fetching transcript ({attempt+1}/{MAX_RETRIES}) via proxy [{instance}] for: {video_id}")
            
            response = requests.get(api_url, timeout=8)
            if response.status_code != 200:
                raise requests.exceptions.HTTPError(f"Proxy status code {response.status_code}")
                
            data = response.json()
            subtitles = data.get("subtitles", [])
            
            if not subtitles:
                raise ValueError("No subtitles array available on this proxy node.")
                
            # Cross-reference the available tracks against your prioritized configuration array
            selected_track = None
            for lang in LANGUAGES:
                selected_track = next((s for s in subtitles if s.get("code") == lang), None)
                if selected_track:
                    break
            
            # Fallback to the absolute first language track if targeted matches aren't online
            if not selected_track:
                selected_track = subtitles[0]
                
            # Download the raw transcript stream file directly
            sub_response = requests.get(selected_track["url"], timeout=8)
            sub_response.raise_for_status()
            
            # Map raw data stream cleanly into structural items list code blocks expect
            parsed_items = parse_vtt_to_items(sub_response.text)
            if not parsed_items:
                raise ValueError("Unable to parse out text intervals from target subtitle file stream.")
                
            return MockTranscriptResponse(parsed_items, language_code=selected_track.get("code", "en"))
            
        except Exception as e:
            last_error = e
            wait = retry_delay(attempt)
            logger.warning(f"Attempt {attempt+1} via proxy failed. Error: {e}. Retrying in {wait:.2f} sec...")
            time.sleep(wait)
            
    raise last_error

# ==========================================
# Get Transcript
# ==========================================
def get_transcript(video_id):
    cleanup_cache()
    cached = get_cached(video_id)
    if cached:
        return cached

    try:
        transcript_data = fetch_with_retry(video_id)
        segments = []
        raw_text = []
        total_words = 0
        total_characters = 0
        total_duration = 0.0

        # This structural computation loop remains exactly how you built it
        for item in transcript_data:
            text = item.text.strip()
            raw_text.append(text)
            total_words += len(text.split())
            total_characters += len(text)
            total_duration = max(
                total_duration,
                item.start + item.duration
            )

            segments.append({
                "text": text,
                "start": round(item.start, 2),
                "duration": round(item.duration, 2)
            })

        result = {
            "success": True,
            "video_id": video_id,
            "language": transcript_data.language_code,
            "segment_count": len(segments),
            "word_count": total_words,
            "character_count": total_characters,
            "duration": round(total_duration, 2),
            "cached": False,
            "raw_text": " ".join(raw_text),
            "segments": segments
        }

        save_cache(video_id, result)
        logger.info(f"Transcript fetched successfully : {video_id}")
        return result
        
    except Exception as e:
        logger.exception(f"Failed to fetch transcript : {video_id}")
        return {
            "success": False,
            "error": str(e)
        }

#             "error": str(e)

#         }
