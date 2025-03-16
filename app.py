from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import openai
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)
CORS(app)  # すべてのオリジン・メソッドを許可

DATA_FILE = "ingredients.json"

# 初回起動時にJSONファイルを作成
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

# 材料の管理（取得, 追加, 削除）
@app.route("/ingredients", methods=["GET", "POST", "DELETE"])
def manage_ingredients():
    with open(DATA_FILE, "r") as f:
        ingredients = json.load(f)

    if request.method == "GET":
        return jsonify(ingredients)

    data = request.json
    ingredient_name = data.get("name")

    if not ingredient_name:
        return jsonify({"error": "材料名が必要です"}), 400

    if request.method == "POST":
        ingredients.append({"name": ingredient_name})

    elif request.method == "DELETE":
        ingredients = [item for item in ingredients if item["name"] != ingredient_name]

    with open(DATA_FILE, "w") as f:
        json.dump(ingredients, f, indent=4)

    return jsonify({"message": "処理が完了しました", "ingredients": ingredients})

# AIで献立を生成
@app.route("/generate_menu", methods=["POST"])
def generate_menu():
    with open(DATA_FILE, "r") as f:
        ingredients = json.load(f)

    ingredient_list = ", ".join([item["name"] for item in ingredients])
    prompt = f"以下の材料を使った献立を考えてください: {ingredient_list}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return jsonify({"menu": response["choices"][0]["message"]["content"]})

if __name__ == "__main__":
    app.run(debug=True)
