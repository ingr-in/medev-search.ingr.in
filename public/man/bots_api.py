from flask import Blueprint, request, jsonify

bots_api = Blueprint("bots_api", __name__)

# 👉 અહીં તમારું crawler code paste કરો (start_crawl, worker, etc.)

@bots_api.route("/bots")
def run_bots():
    mode = request.args.get("sr")

    if mode == "json":
        start_crawl()
        return jsonify({
            "status": "success",
            "total": len(results),
            "data": results
        })

    return "Crawler Running"