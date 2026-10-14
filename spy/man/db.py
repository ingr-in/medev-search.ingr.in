from flask import Flask, Blueprint, jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError, ConfigurationError
from pymongo import ReturnDocument
import os

app = Flask(__name__)

db_route = Blueprint("db_route", __name__)

# MongoDB Atlas connection string
MONGO_URI = os.environ.get("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("MONGO_URI environment variable is missing")

try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # Check connection
    client.admin.command("ping")

    # Database and collection
    database = client["myDatabase"]
    recipes = database["recipes"]

except (ConfigurationError, PyMongoError) as e:
    raise RuntimeError(f"MongoDB connection failed: {e}") from e


@db_route.route("/db", methods=["GET"])
def get_recipes():
    try:
        documents = list(
            recipes.find({}, {"_id": 0})
        )

        return jsonify({
            "success": True,
            "count": len(documents),
            "data": documents
        })

    except PyMongoError:
        return jsonify({
            "success": False,
            "error": "Database operation failed"
        }), 500


@db_route.route("/db/potato", methods=["GET"])
def get_potato_recipe():
    try:
        document = recipes.find_one(
            {"ingredients": "potato"},
            {"_id": 0}
        )

        if document is None:
            return jsonify({
                "success": False,
                "message": "Potato recipe not found"
            }), 404

        return jsonify({
            "success": True,
            "data": document
        })

    except PyMongoError:
        return jsonify({
            "success": False,
            "error": "Database operation failed"
        }), 500


app.register_blueprint(db_route)


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )