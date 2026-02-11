import os
import logging
from flask import Flask, jsonify, request
from datetime import datetime

# ---------------- CONFIG ----------------

APP_NAME = "demo-ci-cd"
APP_VERSION = "1.0.1"

PORT = int(os.getenv("PORT", 5000))
ENV = os.getenv("ENV", "production")

# ---------------- LOGGING ----------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(APP_NAME)

# ---------------- APP ----------------

app = Flask(__name__)


# ---------------- ROUTES ----------------

@app.route("/")
def index():
    return jsonify({
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "time": datetime.utcnow().isoformat()
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "env": ENV
    })


@app.route("/info")
def info():
    return jsonify({
        "client_ip": request.remote_addr,
        "headers": dict(request.headers)
    })


# ---------------- ERROR HANDLING ----------------

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(e):
    logger.exception(e)
    return jsonify({"error": "Internal error"}), 500


# ---------------- START ----------------

if __name__ == "__main__":

    logger.info("=" * 50)
    logger.info("Starting %s", APP_NAME)
    logger.info("Version: %s", APP_VERSION)
    logger.info("Env: %s", ENV)
    logger.info("Port: %s", PORT)
    logger.info("=" * 50)

    app.run(
        host="0.0.0.0",
        port=PORT,
        debug=False
    )

