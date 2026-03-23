from flask import Blueprint, jsonify
from services.api_service import get_data

api_routes = Blueprint("api", __name__)

@api_routes.route("/data")
def data():
    result = get_data()
    return jsonify(result)
