from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "DELETE"]}})

# Gemini API の設定
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY 環境変数が設定されていません。")
genai.configure(api_key=GOOGLE_API_KEY)

models = genai.list_models()
for model in models:
    print(f"Model: {model.name}")
    print(f"  Description: {model.description}")
    print(f"  Supported generation methods: {model.supported_generation_methods}")

DATA_FILE = "ingredients.json"

def load_ingredients():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_ingredients(ingredients):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(ingredients, f, indent=4)

@app.route("/ingredients", methods=["GET", "POST", "DELETE"])
def manage_ingredients():
    ingredients = load_ingredients()
    if request.method == "GET":
        return jsonify(ingredients)
    elif request.method == "POST":
        data = request.get_json()

        ingredient = data.get("name")
        if not ingredient:
            return jsonify({"error": "材料名が必要です"}), 400
        ingredients.append({"name": ingredient})
        save_ingredients(ingredients)
        return jsonify({"message": "材料を追加しました", "ingredients": ingredients})
    elif request.method == "DELETE":
        data = request.get_json()
        ingredient_to_delete = data.get("name")
        if not ingredient_to_delete:
            return jsonify({"error": "削除する材料名が必要です"}), 400
        ingredients = [item for item in ingredients if item["name"] != ingredient_to_delete]
        save_ingredients(ingredients)
        return jsonify({"message": "材料を削除しました", "ingredients": ingredients})

@app.route("/generate_menu", methods=["POST"])
def generate_menu():
    ingredients = load_ingredients()
    if not ingredients:
        return jsonify({"error": "食材が登録されていません"}), 400

    ingredient_list = ", ".join([item["name"] for item in ingredients])
    prompt = f"以下の材料を使った簡単で栄養バランスの良い献立を2つ提案してください: {ingredient_list}"

    try:
        response = model.generate_content(prompt)
        menu = response.text.strip()
        return jsonify({"menu": menu})
    except Exception as e:
        print(f"Gemini API エラー: {e}")
        return jsonify({"error": "献立生成に失敗しました"}), 500

if __name__ == "__main__":
    app.run(debug=True)