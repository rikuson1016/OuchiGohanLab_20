from flask import Flask, request, jsonify
from flask_cors import CORS  # CORSを扱うためのライブラリをインポート
import json
import os
import openai
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# OpenAI APIキーの設定
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# CORS設定（特定のオリジンを許可）
CORS(app, resources={r"/*": {"origins": "http://localhost:5173", "methods": ["GET", "POST", "DELETE"]}})

DATA_FILE = "ingredients.json"

# ✅ JSONファイルの読み込み関数
def load_ingredients():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# ✅ JSONファイルへの書き込み関数
def save_ingredients(ingredients):
    with open(DATA_FILE, "w") as f:
        json.dump(ingredients, f, indent=4)

# "/ingredients" エンドポイント（GET, POST, DELETEに対応）
@app.route("/ingredients", methods=["GET", "POST", "DELETE"])
def manage_ingredients():
    try:
        if request.method == "GET":
            return jsonify(load_ingredients())

        elif request.method == "POST":
            data = request.json
            ingredient = data.get("name")
            if not ingredient:
                return jsonify({"error": "材料名が必要です"}), 400

            ingredients = load_ingredients()
            ingredients.append({"name": ingredient})
            save_ingredients(ingredients)

            return jsonify({"message": "材料を追加しました", "ingredients": ingredients})

        elif request.method == "DELETE":
            data = request.json
            ingredient_to_delete = data.get("name")

            if not ingredient_to_delete:
                return jsonify({"error": "削除する材料名が必要です"}), 400

            ingredients = load_ingredients()
            ingredients = [item for item in ingredients if item["name"] != ingredient_to_delete]
            save_ingredients(ingredients)

            return jsonify({"message": "材料を削除しました", "ingredients": ingredients})

    except Exception as e:
        print(f"エラー発生: {str(e)}")
        return jsonify({"error": str(e)}), 500

# OpenAIを利用して献立を生成するエンドポイント
@app.route("/generate_menu", methods=["POST"])
def generate_menu():
    with open(DATA_FILE, "r") as f:
        ingredients = json.load(f)

    ingredient_list = ", ".join([item["name"] for item in ingredients])
    prompt = f"以下の材料を使った献立を考えてください: {ingredient_list}"

    try:
        # 新しいインターフェースを使用
        response = openai.Completion.create(
            model="gpt-3.5-turbo",  # モデルを選択
            prompt=prompt,           # プロンプトを指定
            max_tokens=100           # 最大トークン数（オプション）
        )

        menu = response.choices[0].text.strip()  # レスポンスから結果を取得

        return jsonify({"menu": menu})
    except Exception as e:
        return jsonify({"error": "内部エラーが発生しました。"}), 500

# Flaskアプリの起動（デバッグモード）
if __name__ == "__main__":
    app.run(debug=True)
