from flask import Blueprint, jsonify
from services.api_service import get_data

api = Blueprint("api", __name__)

@api.route("/data")
def data():
    result = get_data()
    return jsonify(result)
