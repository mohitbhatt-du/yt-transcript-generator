import logging
import random
import threading
import time

from youtube_transcript_api import YouTubeTranscriptApi


# ==========================================
# Configuration
# ==========================================

MAX_RETRIES = 3

CACHE_TTL = 60 * 60 * 24      # 24 Hours

BASE_BACKOFF = 1.0

LANGUAGES = [

    "hi",
    "en",
    "en-US",
    "hi-IN"

]


# ==========================================
# Logging
# ==========================================

logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)


# ==========================================
# In-Memory Cache
# ==========================================

cache = {}

cache_lock = threading.Lock()


# cache format
#
# cache = {
#
#     video_id:{
#
#         "timestamp":123456,
#
#         "data":{...}
#
#     }
#
# }


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


# ==========================================
# Cache Cleanup
# ==========================================

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

        logger.info(

            f"Removed {len(expired)} expired cache entries."

        )


# ==========================================
# Retry Delay
# ==========================================

def retry_delay(attempt):

    delay = BASE_BACKOFF * (2 ** attempt)

    jitter = random.uniform(0.0, 0.5)

    return delay + jitter


# ==========================================
# Fetch With Retry
# ==========================================

def fetch_with_retry(video_id):

    last_error = RuntimeError("Transcript fetch failed.")

    for attempt in range(MAX_RETRIES):

        try:

            logger.info(
                f"Fetching transcript ({attempt+1}/{MAX_RETRIES}) : {video_id}"
            )

            return YouTubeTranscriptApi().fetch(
                video_id,
                languages=LANGUAGES
            )

        except Exception as e:

            last_error = e

            wait = retry_delay(attempt)

            logger.warning(
                f"Attempt {attempt+1} failed. Retrying in {wait:.2f} sec..."
            )

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

        logger.info(

            f"Transcript fetched successfully : {video_id}"

        )

        return result

    except Exception as e:

        logger.exception(

            f"Failed to fetch transcript : {video_id}"

        )

        return {

            "success": False,

            "error": str(e)

        }
