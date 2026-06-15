from flask import Blueprint, jsonify
#from services.api_service import get_data
def get_data():
    return {
        "status": "success",
        "data": [1, 2, 3, 4]
    }
api = Blueprint("api", __name__)

@api.route("/data")
def data():
    result = get_data()
    return jsonify(result)
