import os
from flask import Blueprint, jsonify, request
from pymongo import MongoClient, ReturnDocument
from pymongo.errors import PyMongoError, ConfigurationError
from urllib.parse import quote_plus

# --------------------------------------------------
# BLUEPRINT
# --------------------------------------------------

db = Blueprint("db", __name__)

# --------------------------------------------------
# MONGODB ATLAS CONFIGURATION
# --------------------------------------------------
# Option 1: Environment variable MONGO_URI
# Option 2: Demo username/password below
#
# Replace demo credentials with your own credentials.
# Never publish real credentials in a public repository.
# --------------------------------------------------

MONGO_USERNAME = "YOUR_MONGODB_USERNAME"
MONGO_PASSWORD = "YOUR_MONGODB_PASSWORD"

MONGO_HOST = "cluster0.example.mongodb.net"
MONGO_DATABASE = "myDatabase"

# Encode username/password to handle special characters.
username = quote_plus(MONGO_USERNAME)
password = quote_plus(MONGO_PASSWORD)

DEMO_URI = (
    f"mongodb+srv://{username}:{password}"
    f"@{MONGO_HOST}/?retryWrites=true&w=majority"
)

# Prefer MONGO_URI from Render Environment if configured.
MONGO_URI = os.environ.get("MONGO_URI") or DEMO_URI

# Do not connect when placeholder credentials are still present.
DEMO_CREDENTIALS = (
    MONGO_USERNAME == "if0_38703354"
    or MONGO_PASSWORD == "ZYqQXt7j8kU3BXq6"
    or MONGO_HOST == "cluster0.wih1ej0.mongodb.net"
)

client = None
database = None
recipes = None


# --------------------------------------------------
# CONNECT TO MONGODB
# --------------------------------------------------

def connect_mongodb():
    global client, database, recipes

    if DEMO_CREDENTIALS and not os.environ.get("MONGO_URI"):
        raise RuntimeError(
            "Configure MONGO_URI or replace demo MongoDB credentials"
        )

    if not MONGO_URI:
        raise RuntimeError("MongoDB URI is missing")

    if client is None:
        client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )

    # Verify connectivity.
    client.admin.command("ping")

    database = client[MONGO_DATABASE]
    recipes = database["recipes"]


# --------------------------------------------------
# ERROR RESPONSE
# --------------------------------------------------

def database_error(message, status=500):
    return jsonify({
        "success": False,
        "error": message
    }), status


def handle_db_error(exc):
    if isinstance(exc, RuntimeError):
        return database_error(str(exc), 503)

    if isinstance(exc, (ConfigurationError, PyMongoError)):
        # Keep credentials and internal connection details private.
        return database_error("MongoDB operation failed", 503)

    return database_error("Internal server error", 500)


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
            "database": MONGO_DATABASE,
            "collection": "recipes",
            "version": "1.0.0"
        })

    except (RuntimeError, ConfigurationError, PyMongoError) as exc:
        return handle_db_error(exc)


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

    except (RuntimeError, ConfigurationError, PyMongoError) as exc:
        return handle_db_error(exc)


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

    except (RuntimeError, ConfigurationError, PyMongoError) as exc:
        return handle_db_error(exc)


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

    except (RuntimeError, ConfigurationError, PyMongoError) as exc:
        return handle_db_error(exc)


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
        return database_error(
            "A valid JSON object is required",
            400
        )

    name = data.get("name")
    ingredients = data.get("ingredients")
    prep_time = data.get("prep_time")

    if not isinstance(name, str) or not name.strip():
        return database_error(
            "A valid recipe name is required",
            400
        )

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

        # Prevent duplicate recipe names.
        if recipes.find_one({"name": document["name"]}):
            return database_error(
                "A recipe with this name already exists",
                409
            )

        result = recipes.insert_one(document)

        return jsonify({
            "success": True,
            "message": "Recipe inserted successfully",
            "inserted_id": str(result.inserted_id)
        }), 201

    except (RuntimeError, ConfigurationError, PyMongoError) as exc:
        return handle_db_error(exc)


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
        return database_error(
            "A valid JSON object is required",
            400
        )

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

    except (RuntimeError, ConfigurationError, PyMongoError) as exc:
        return handle_db_error(exc)


# --------------------------------------------------
# DELETE RECIPE
# DELETE /db/recipes/<name>
# --------------------------------------------------

@db.route("/recipes/<string:name>", methods=["DELETE"])
def delete_recipe(name):
    try:
        connect_mongodb()

        result = recipes.delete_one({"name": name})

        if result.deleted_count == 0:
            return database_error("Recipe not found", 404)

        return jsonify({
            "success": True,
            "message": "Recipe deleted successfully",
            "deleted_count": result.deleted_count
        })

    except (RuntimeError, ConfigurationError, PyMongoError) as exc:
        return handle_db_error(exc)