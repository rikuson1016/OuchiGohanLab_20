from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DATA_FILE = "ingredients.json"

# 初回起動時にJSONファイルがない場合は作成
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# 材料を取得するAPI
@app.route("/ingredients", methods=["GET"])
def get_ingredients():
    with open(DATA_FILE, "r") as f:
        ingredients = json.load(f)
    return jsonify(ingredients)

# 材料を追加するAPI
@app.route("/ingredients", methods=["POST"])
def add_ingredient():
    data = request.json
    ingredient = data.get("name")

    if not ingredient:
        return jsonify({"error": "材料名が必要です"}), 400

    with open(DATA_FILE, "r") as f:
        ingredients = json.load(f)

    ingredients.append({"name": ingredient})

    with open(DATA_FILE, "w") as f:
        json.dump(ingredients, f, indent=4)

    return jsonify({"message": "材料を追加しました", "ingredients": ingredients})

if __name__ == "__main__":
    app.run(debug=True)
