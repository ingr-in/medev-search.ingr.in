import os

from flask import Blueprint, jsonify, request
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError, ConfigurationError

# Blueprint
db = Blueprint("db", __name__)

# MongoDB Atlas configuration
MONGO_URI = os.environ.get("mongodb+srv://if0_38703354:ZYqQXt7j8kU3BXq6@cluster0.wih1ej0.mongodb.net/")

client = None
database = None
recipes = None


# --------------------------------------------------
# CONNECT TO MONGODB
# --------------------------------------------------

def connect_mongodb():
    global client, database, recipes

    if not MONGO_URI:
        raise RuntimeError("MONGO_URI environment variable is missing")

    if client is None:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000
        )

    # Verify database connectivity
    client.admin.command("ping")

    database = client["myDatabase"]
    recipes = database["recipes"]


# --------------------------------------------------
# ERROR RESPONSE
# --------------------------------------------------

def database_error(message, status=500):
    return jsonify({
        "success": False,
        "error": message
    }), status


# --------------------------------------------------
# DATABASE STATUS
# GET /db
# GET /db/
# --------------------------------------------------

@db.route("", methods=["GET"])
@db.route("/", methods=["GET"])
def database_home():
    try:
        connect_mongodb()

        return jsonify({
            "success": True,
            "message": "MongoDB connection successful",
            "status": "running",
            "database": "myDatabase",
            "collection": "recipes",
            "version": "1.0.0"
        })

    except RuntimeError:
        return database_error(
            "MONGO_URI environment variable is missing",
            503
        )

    except ConfigurationError:
        return database_error(
            "Invalid MongoDB connection configuration",
            503
        )

    except PyMongoError:
        return database_error(
            "MongoDB connection failed",
            503
        )


# --------------------------------------------------
# PING DATABASE
# GET /db/ping
# --------------------------------------------------

@db.route("/ping", methods=["GET"])
def ping_db():
    try:
        connect_mongodb()

        return jsonify({
            "success": True,
            "ok": True,
            "message": "MongoDB is reachable"
        })

    except RuntimeError:
        return database_error(
            "MONGO_URI environment variable is missing",
            503
        )

    except (ConfigurationError, PyMongoError):
        return database_error(
            "MongoDB is not reachable",
            503
        )


# --------------------------------------------------
# READ ALL RECIPES
# GET /db/recipes
# --------------------------------------------------

@db.route("/recipes", methods=["GET"])
def get_recipes():
    try:
        connect_mongodb()

        documents = list(
            recipes.find({}, {"_id": 0}).limit(500)
        )

        return jsonify({
            "success": True,
            "count": len(documents),
            "data": documents
        })

    except RuntimeError:
        return database_error("MongoDB configuration is missing", 503)

    except (ConfigurationError, PyMongoError):
        return database_error("Unable to read recipes")


# --------------------------------------------------
# FIND RECIPE BY NAME
# GET /db/recipes/<name>
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
            return database_error("Recipe not found", 404)

        return jsonify({
            "success": True,
            "data": document
        })

    except RuntimeError:
        return database_error("MongoDB configuration is missing", 503)

    except (ConfigurationError, PyMongoError):
        return database_error("Unable to find recipe")


# --------------------------------------------------
# INSERT RECIPE
# POST /db/recipes
# --------------------------------------------------

@db.route("/recipes", methods=["POST"])
def insert_recipe():
    if not request.is_json:
        return database_error(
            "Content-Type must be application/json",
            400
        )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return database_error("A valid JSON object is required", 400)

    name = data.get("name")
    ingredients = data.get("ingredients")
    prep_time = data.get("prep_time")

    if not isinstance(name, str) or not name.strip():
        return database_error("A valid recipe name is required", 400)

    if (
        not isinstance(ingredients, list)
        or not all(isinstance(item, str) for item in ingredients)
    ):
        return database_error(
            "ingredients must be a list of strings",
            400
        )

    if (
        not isinstance(prep_time, int)
        or isinstance(prep_time, bool)
        or prep_time < 0
    ):
        return database_error(
            "prep_time must be a non-negative integer",
            400
        )

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

    except RuntimeError:
        return database_error("MongoDB configuration is missing", 503)

    except (ConfigurationError, PyMongoError):
        return database_error("Unable to insert recipe")


# --------------------------------------------------
# UPDATE RECIPE
# PUT /db/recipes/<name>
# --------------------------------------------------

@db.route("/recipes/<string:name>", methods=["PUT"])
def update_recipe(name):
    if not request.is_json:
        return database_error(
            "Content-Type must be application/json",
            400
        )

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return database_error("A valid JSON object is required", 400)

    allowed_fields = {"ingredients", "prep_time"}

    if not data or not set(data).issubset(allowed_fields):
        return database_error(
            "Only ingredients and prep_time can be updated",
            400
        )

    if "ingredients" in data:
        ingredients = data["ingredients"]

        if (
            not isinstance(ingredients, list)
            or not all(isinstance(item, str) for item in ingredients)
        ):
            return database_error(
                "ingredients must be a list of strings",
                400
            )

    if "prep_time" in data:
        prep_time = data["prep_time"]

        if (
            not isinstance(prep_time, int)
            or isinstance(prep_time, bool)
            or prep_time < 0
        ):
            return database_error(
                "prep_time must be a non-negative integer",
                400
            )

    try:
        connect_mongodb()

        document = recipes.find_one_and_update(
            {"name": name},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
            projection={"_id": 0}
        )

        if document is None:
            return database_error("Recipe not found", 404)

        return jsonify({
            "success": True,
            "message": "Recipe updated successfully",
            "data": document
        })

    except RuntimeError:
        return database_error("MongoDB configuration is missing", 503)

    except (ConfigurationError, PyMongoError):
        return database_error("Unable to update recipe")


# --------------------------------------------------
# DELETE RECIPE
# DELETE /db/recipes/<name>
# --------------------------------------------------

@db.route("/recipes/<string:name>", methods=["DELETE"])
