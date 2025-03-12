from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "DELETE"]}})

DATA_FILE = "ingredients.json"

# 初回起動時にJSONファイルがない場合は作成
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

@app.route("/ingredients", methods=["GET", "POST", "DELETE"])
def manage_ingredients():
    if request.method == "GET":
        with open(DATA_FILE, "r") as f:
            ingredients = json.load(f)
        return jsonify(ingredients)

    elif request.method == "POST":
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

    elif request.method == "DELETE":
        data = request.json
        ingredient_to_delete = data.get("name")

        if not ingredient_to_delete:
            return jsonify({"error": "削除する材料名が必要です"}), 400

        with open(DATA_FILE, "r") as f:
            ingredients = json.load(f)

        # 材料を削除
        ingredients = [item for item in ingredients if item["name"] != ingredient_to_delete]

        with open(DATA_FILE, "w") as f:
            json.dump(ingredients, f, indent=4)

        return jsonify({"message": "材料を削除しました", "ingredients": ingredients})


if __name__ == "__main__":
    app.run(debug=True)

import openai  # 追加
from dotenv import load_dotenv  # APIキーを環境変数で管理
import os

load_dotenv()  # .envファイルから環境変数を読み込む

openai.api_key = os.getenv("OPENAI_API_KEY")  # APIキーを設定

# 献立を生成するAPI
@app.route("/generate_menu", methods=["POST"])
def generate_menu():
    with open(DATA_FILE, "r") as f:
        ingredients = json.load(f)

    ingredient_list = ", ".join([item["name"] for item in ingredients])

    prompt = f"以下の材料を使った献立を考えてください: {ingredient_list}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # モデルを選択（GPT-4を使う場合は変更）
        messages=[{"role": "user", "content": prompt}]
    )

    menu = response["choices"][0]["message"]["content"]
    
    return jsonify({"menu": menu})

