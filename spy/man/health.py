from flask import Blueprint
from datetime import datetime

health = Blueprint("health", __name__)

@health.route("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }, 200
