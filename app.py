# 必要なモジュールをインポート
from flask import Flask, request, jsonify  # Flask本体とリクエスト/レスポンス処理用
from flask_cors import CORS  # クロスオリジンリクエストを許可
import google.generativeai as genai  # Gemini API用
import os  # 環境変数取得用
import json  # JSONデータの読み書き用
from dotenv import load_dotenv  # .envファイルから環境変数を読み込む

# .envファイルから環境変数を読み込み
load_dotenv()

# デバッグ用：環境情報を確認
print(f"Current working directory: {os.getcwd()}")  # 実行ディレクトリを表示
print(f"GOOGLE_API_KEY from os.getenv: {os.getenv('GOOGLE_API_KEY')[:5]}...")  # キーの一部を表示（秘匿）
print(f".env file exists: {os.path.exists('.env')}")  # .envファイルの存在確認

# Gemini APIキーを取得
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEYが設定されていません。環境変数または.envファイルを確認してください。")

# Gemini APIを初期化
genai.configure(api_key=GOOGLE_API_KEY)

# 使用可能なモデルをリストアップ（デバッグ用）
print("Available models:")
for m in genai.list_models():
    print(f"  Model: {m.name}, Methods: {m.supported_generation_methods}")

# Geminiモデルを明示的に初期化
model = genai.GenerativeModel("gemini-1.5-flash")  # gemini-1.5-flashを使用（軽量で無料枠に適している）

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# CORS設定：任意のオリジンを許可（開発用）
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "DELETE"]}})

# 食材データを保存するJSONファイルのパス
DATA_FILE = "ingredients.json"

# 食材データをJSONファイルから読み込む関数
def load_ingredients():
    try:
        # ファイルを読み込んでJSONとしてパース
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # ファイルがないか壊れている場合は空リストを返す
        print(f"食材読み込みエラー: {e}")
        return []

# 食材データをJSONファイルに保存する関数
def save_ingredients(ingredients):
    try:
        # ファイルを書き込みモードで開き、JSON形式で保存
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(ingredients, f, indent=4)
    except Exception as e:
        # 保存エラーをログに記録
        print(f"食材保存エラー: {e}")

# "/ingredients"エンドポイント：食材の取得（GET）、追加（POST）、削除（DELETE）を処理
@app.route("/ingredients", methods=["GET", "POST", "DELETE"])
def manage_ingredients():
    try:
        # 現在の食材リストを読み込む
        ingredients = load_ingredients()

        # GETリクエスト：食材リストを返す
        if request.method == "GET":
            return jsonify(ingredients)

        # POSTリクエスト：新しい食材を追加
        elif request.method == "POST":
            data = request.get_json()
            ingredient = data.get("name")
            if not ingredient:
                return jsonify({"error": "材料名が必要です"}), 400
            ingredients.append({"name": ingredient})
            save_ingredients(ingredients)
            return jsonify({"message": "材料を追加しました", "ingredients": ingredients})

        # DELETEリクエスト：指定した食材を削除
        elif request.method == "DELETE":
            data = request.get_json()
            ingredient_to_delete = data.get("name")
            if not ingredient_to_delete:
                return jsonify({"error": "削除する材料名が必要です"}), 400
            ingredients = [item for item in ingredients if item["name"] != ingredient_to_delete]
            save_ingredients(ingredients)
            return jsonify({"message": "材料を削除しました", "ingredients": ingredients})

    except Exception as e:
        print(f"エラー発生（manage_ingredients）: {e}")
        return jsonify({"error": "サーバーエラーが発生しました"}), 500

# "/generate_menu"エンドポイント：Gemini APIを使って献立を生成
@app.route("/generate_menu", methods=["POST"])
def generate_menu():
    try:
        # 現在の食材リストを読み込む
        ingredients = load_ingredients()
        print(f"Loaded ingredients: {ingredients}")
        if not ingredients:
            return jsonify({"error": "食材が登録されていません"}), 400

        # 食材リストをカンマ区切りの文字列に変換
        ingredient_list = ", ".join([item["name"] for item in ingredients])
        # 改良したプロンプトを作成
        prompt = (
            f"あなたは日本の家庭料理に精通したシェフです。以下の材料を使って、簡単で栄養バランスの良い2つの献立を提案してください。"
            f"各献立には、料理名、簡単な作り方（3～5ステップ）、特徴（味や栄養面）を記載してください。"
            f"調理時間は20分以内で、日本の家庭で一般的な調味料（醤油、塩、砂糖、油など）を使用してください。"
            f"材料：{ingredient_list}"
        )
        print(f"Prompt: {prompt}")

        # Gemini APIで献立を生成
        print("Generating menu with Gemini...")
        response = model.generate_content(prompt)
        menu = response.text.strip()
        print(f"Generated menu: {menu}")

        # 献立をJSON形式で返す
        return jsonify({"menu": menu})

    except Exception as e:
        print(f"エラー発生（generate_menu）: {type(e).__name__}: {e}")
        return jsonify({"error": f"献立生成に失敗しました: {str(e)}"}), 500

# アプリケーションをデバッグモードで起動
if __name__ == "__main__":
    app.run(debug=True)