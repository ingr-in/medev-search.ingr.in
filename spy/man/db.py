from flask import Flask, jsonify
from pymongo import MongoClient
import 
db = Blueprint("db", __name__)

app = Flask(__name__)
mongo_uri = "mongodb+srv://if0_38703354:ZYqQXt7j8kU3BXq6@cluster0.wih1ej0.mongodb.net/"
client = MongoClient(mongo_uri)

@app.route("/ping-db")
def ping_db():
    try:
        client.admin.command("ping")
        return jsonify({"ok": True, "message": "MongoDB is reachable"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/db")
def index():
    return "Flask + MongoDB is running. Try GET /ping-db"

if __name__ == "__main__":
    app.run() --------------------------------------------------
# DATABASE STATUS
# URL: /db
# --------------------------------------------------

@db.route("", methods=["GET"])
@db.route("/", methods=["GET"])
def database_home():
    try:
        connect_mongodb()

        return jsonify({
            "message": "MongoDB connection successful",
            "status": "running",
            "database": "myDatabase",
            "collection": "recipes",
            "version": "1.0.0"
        })

    except ConfigurationError:
        return database_error("Invalid MongoDB connection configuration")

    except PyMongoError:
        return database_error("MongoDB connection failed")

    except RuntimeError:
        return database_error("MONGO_URI environment variable is missing")


# --------------------------------------------------
# READ ALL RECIPES
# URL: /db/recipes
# --------------------------------------------------

@db.route("/recipes", methods=["GET"])
def get_recipes():
    try:
        connect_mongodb()

        documents = list(
            recipes.find({}, {"_id": 0})
        )

        return jsonify({
            "success": True,
            "count": len(documents),
            "data": documents
        })

    except (PyMongoError, ConfigurationError):
        return database_error("Unable to read recipes")

    except RuntimeError:
        return database_error("MongoDB configuration is missing")


# --------------------------------------------------
# FIND RECIPE BY NAME
# URL: /db/recipes/<name>
# --------------------------------------------------

@db.route("/recipes/<string:name>", methods=["GET"])
def get_recipe(name):
    try:
        connect_mongodb()

        document = recipes.find_one(
            {"name": name},
            {"_id": 0}
        )

        if document is None:
            return jsonify({
                "success": False,
                "message": "Recipe not found"
            }), 404

        return jsonify({
            "success": True,
            "data": document
        })

    except (PyMongoError, ConfigurationError):
        return database_error("Unable to find recipe")

    except RuntimeError:
        return database_error("MongoDB configuration is missing")


# --------------------------------------------------
# INSERT RECIPE
# URL: POST /db/recipes
# --------------------------------------------------

@db.route("/recipes", methods=["POST"])
def insert_recipe():
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Content-Type must be application/json"
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "A valid JSON object is required"
        }), 400

    name = data.get("name")
    ingredients = data.get("ingredients")
    prep_time = data.get("prep_time")

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "success": False,
            "error": "A valid recipe name is required"
        }), 400

    if (
        not isinstance(ingredients, list)
        or not all(isinstance(item, str) for item in ingredients)
    ):
        return jsonify({
            "success": False,
            "error": "ingredients must be a list of strings"
        }), 400

    if (
        not isinstance(prep_time, int)
        or isinstance(prep_time, bool)
        or prep_time < 0
    ):
        return jsonify({
            "success": False,
            "error": "prep_time must be a non-negative integer"
        }), 400

    document = {
        "name": name.strip(),
        "ingredients": ingredients,
        "prep_time": prep_time
    }

    try:
        connect_mongodb()

        result = recipes.insert_one(document)

        return jsonify({
            "success": True,
            "message": "Recipe inserted successfully",
            "inserted_id": str(result.inserted_id)
        }), 201

    except (PyMongoError, ConfigurationError):
        return database_error("Unable to insert recipe")

    except RuntimeError:
        return database_error("MongoDB configuration is missing")


# --------------------------------------------------
# UPDATE RECIPE
# URL: PUT /db/recipes/<name>
# --------------------------------------------------

@db.route("/recipes/<string:name>", methods=["PUT"])
def update_recipe(name):
    if not request.is_json:
        return jsonify({
            "success": False,
            "error": "Content-Type must be application/json"
        }), 400

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "error": "A valid JSON object is required"
        }), 400

    allowed_fields = {"ingredients", "prep_time"}

    if not data or not set(data.keys()).issubset(allowed_fields):
        return jsonify({
            "success": False,
            "error": "Only ingredients and prep_time can be updated"
        }), 400

    if "ingredients" in data:
        ingredients = data["ingredients"]

        if (
            not isinstance(ingredients, list)
            or not all(isinstance(item, str) for item in ingredients)
        ):
            return jsonify({
                "success": False,
                "error": "ingredients must be a list of strings"
            }), 400

    if "prep_time" in data:
        prep_time = data["prep_time"]

        if (
            not isinstance(prep_time, int)
            or isinstance(prep_time, bool)
            or prep_time < 0
        ):
            return jsonify({
                "success": False,
                "error": "prep_time must be a non-negative integer"
            }), 400

    try:
        connect_mongodb()

        document = recipes.find_one_and_update(
            {"name": name},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
            projection={"_id": 0}
        )

        if document is None:
            return jsonify({
                "success": False,
                "message": "Recipe not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Recipe updated successfully",
            "data": document
        })

    except (PyMongoError, ConfigurationError):
        return database_error("Unable to update recipe")

    except RuntimeError:
        return database_error("MongoDB configuration is missing")


# --------------------------------------------------
# DELETE RECIPE
# URL: DELETE /db/recipes/<name>
# --------------------------------------------------

@db.route("/recipes/<string:name>", methods=["DELETE"])
def delete_recipe(name):
    try:
        connect_mongodb()

        result = recipes.delete_one({
            "name": name
        })

        if result.deleted_count == 0:
            return jsonify({
                "success": False,
                "message": "Recipe not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Recipe deleted successfully"
        })

    except (PyMongoError, ConfigurationError):
        return database_error("Unable to delete recipe")

    except RuntimeError:
        return database_error("MongoDB configuration is missing")