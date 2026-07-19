import logging
import os
from urllib.parse import urlparse, parse_qs

from flask import Flask, jsonify, render_template, request
from flask_limiter import Limiter
from werkzeug.middleware.proxy_fix import ProxyFix

from services.transcript import get_transcript

# ==========================================================
# Flask App
# ==========================================================

app = Flask(__name__)

# Maximum request size (1 MB)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024

# Trust one reverse proxy (Cloudflare)
app.wsgi_app = ProxyFix(
    app.wsgi_app,
    x_for=1,
    x_proto=1,
    x_host=1,
)

# ==========================================================
# Logging
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)

# ==========================================================
# Cloudflare Real IP
# ==========================================================


def cloudflare_ip():
    """
    Returns the real client IP.

    Works locally and behind Cloudflare.
    """

    return (
        request.headers.get("CF-Connecting-IP")
        or request.remote_addr
    )


# ==========================================================
# Rate Limiter
# ==========================================================

limiter = Limiter(
    key_func=cloudflare_ip,
    app=app,
    default_limits=[]
)

# ==========================================================
# Routes
# ==========================================================


@app.route("/")
@limiter.exempt
def home():
    return render_template("index.html")


@app.route("/health")
@limiter.exempt
def health():

    return jsonify({
        "status": "ok",
        "service": "YT Subtitle Generator"
    })


# ==========================================================
# Extract Video ID
# ==========================================================


def extract_video_id(url):

    try:

        parsed = urlparse(url)

        hostname = parsed.hostname or ""

        if hostname in (
            "youtu.be",
            "www.youtu.be",
        ):
            return parsed.path.lstrip("/")

        if hostname in (
            "youtube.com",
            "www.youtube.com",
            "m.youtube.com",
        ):

            if parsed.path == "/watch":
                return parse_qs(parsed.query).get("v", [None])[0]

            if parsed.path.startswith("/shorts/"):
                return parsed.path.split("/")[2]

            if parsed.path.startswith("/embed/"):
                return parsed.path.split("/")[2]

        return None

    except Exception:

        return None


# ==========================================================
# Transcript API
# ==========================================================


@app.route("/api/transcript", methods=["POST"])
@limiter.limit("2 per minute;10 per day")
def transcript():

    try:

        data = request.get_json(silent=True)

        if not data:

            return jsonify({

                "success": False,

                "error": "Invalid JSON body."

            }), 400

        url = data.get("url", "").strip()

        if not url:

            return jsonify({

                "success": False,

                "error": "YouTube URL is required."

            }), 400

        video_id = extract_video_id(url)

        if not video_id:

            return jsonify({

                "success": False,

                "error": "Invalid YouTube URL."

            }), 400

        logger.info(
            f"Transcript request : {video_id}"
        )

        result = get_transcript(video_id)

        return jsonify(result)

    except Exception as e:

        logger.exception("Unexpected server error")

        return jsonify({

            "success": False,

            "error": "Internal server error.",

            "details": str(e)

        }), 500


# ==========================================================
# Error Handlers
# ==========================================================


@app.errorhandler(429)
def rate_limit(e):

    return jsonify({

        "success": False,

        "error": "Rate limit exceeded.",

        "message": "Maximum 10 transcript requests per day and 2 per minute."

    }), 429


@app.errorhandler(404)
def not_found(e):

    return jsonify({

        "success": False,

        "error": "Endpoint not found."

    }), 404


@app.errorhandler(405)
def method_not_allowed(e):

    return jsonify({

        "success": False,

        "error": "Method not allowed."

    }), 405


@app.errorhandler(500)
def internal_error(e):

    return jsonify({

        "success": False,

        "error": "Internal server error."

    }), 500


# ==========================================================
# Security Headers
# ==========================================================


@app.after_request
def security_headers(response):

    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "geolocation=(), microphone=(), camera=()"
    )

    return response


# ==========================================================
# Run
# ==========================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=int(os.getenv("PORT", 5000)),

        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true",

    )