# 必要なモジュールをインポート
from flask import Flask, request, jsonify  # Flask本体とリクエスト/レスポンス処理用
from flask_cors import CORS  # クロスオリジンリクエストを許可
import json  # JSONデータの読み書き用
import os  # ファイル操作や環境変数取得用
from transformers import pipeline  # ローカルでモデルを動かすためのライブラリ
from dotenv import load_dotenv  # .envファイルから環境変数を読み込む（今回は不要だが残す）

# .envファイルから環境変数を読み込み（必要に応じて使用）
load_dotenv()

# デバッグ用：環境情報を確認
print(f"Current working directory: {os.getcwd()}")  # 実行ディレクトリを表示
print(f".env file exists: {os.path.exists('.env')}")  # .envファイルの存在確認（必須ではない）

# テキスト生成パイプラインをグローバルに初期化（アプリ起動時に一度だけロード）
print("Loading distilgpt2 model...")
generator = pipeline("text-generation", model="distilgpt2")
print("Model loaded successfully")

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# CORS設定：Vue.jsの開発サーバー（localhost:5173）を許可
CORS(app, resources={r"/*": {"origins": os.getenv("CORS_ORIGIN", "http://localhost:5173"), "methods": ["GET", "POST", "DELETE"]}})

# 食材データを保存するJSONファイルのパス
DATA_FILE = "ingredients.json"

# 食材データをJSONファイルから読み込む関数
def load_ingredients():
    # ファイルが存在しない場合は空リストを返す
    if not os.path.exists(DATA_FILE):
        print(f"{DATA_FILE}が存在しません。空リストを返します。")
        return []
    try:
        # ファイルを読み込んでJSONとしてパース
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        # JSONが壊れている場合はエラーをログに記録し空リストを返す
        print(f"JSONデコードエラー: {e}")
        return []
    except PermissionError as e:
        # アクセス権限エラーの場合もログに記録
        print(f"ファイルアクセスエラー: {e}")
        return []

# 食材データをJSONファイルに保存する関数
def save_ingredients(ingredients):
    try:
        # ファイルを書き込みモードで開き、JSON形式で保存（インデント付きで可読性向上）
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
            # リクエストからJSONデータを取得
            data = request.get_json()
            ingredient = data.get("name")
            # 食材名が空の場合はエラーを返す
            if not ingredient:
                return jsonify({"error": "材料名が必要です"}), 400
            # 食材をリストに追加
            ingredients.append({"name": ingredient})
            save_ingredients(ingredients)
            # 成功メッセージと更新後のリストを返す
            return jsonify({"message": "材料を追加しました", "ingredients": ingredients})

        # DELETEリクエスト：指定した食材を削除
        elif request.method == "DELETE":
            # リクエストから削除対象の食材名を取得
            data = request.get_json()
            ingredient_to_delete = data.get("name")
            # 食材名が空の場合はエラーを返す
            if not ingredient_to_delete:
                return jsonify({"error": "削除する材料名が必要です"}), 400
            # 指定した食材をリストから除外
            ingredients = [item for item in ingredients if item["name"] != ingredient_to_delete]
            save_ingredients(ingredients)
            # 成功メッセージと更新後のリストを返す
            return jsonify({"message": "材料を削除しました", "ingredients": ingredients})

    except Exception as e:
        # 予期しないエラーをログに出力し、エラーメッセージを返す
        print(f"エラー発生（manage_ingredients）: {e}")
        return jsonify({"error": "サーバーエラーが発生しました"}), 500

# "/generate_menu"エンドポイント：ローカルのdistilgpt2を使って献立を生成
@app.route("/generate_menu", methods=["POST"])
def generate_menu():
    try:
        # 現在の食材リストを読み込む
        ingredients = load_ingredients()
        print(f"Loaded ingredients: {ingredients}")
        # 食材が空の場合はエラーを返す
        if not ingredients:
            return jsonify({"error": "食材が登録されていません"}), 400

        # 食材リストをカンマ区切りの文字列に変換
        ingredient_list = ", ".join([item["name"] for item in ingredients])
        # モデルに渡すプロンプトを作成
        prompt = f"以下の材料を使った簡単で栄養バランスの良い献立を2つ提案してください: {ingredient_list}"
        print(f"Prompt: {prompt}")

        # ローカルでdistilgpt2を使って献立を生成
        print("Generating menu with distilgpt2...")
        results = generator(prompt, max_length=300, num_return_sequences=1, do_sample=True, top_k=50)
        menu = results[0]["generated_text"].strip()
        print(f"Generated menu: {menu}")

        # 献立をJSON形式で返す
        return jsonify({"menu": menu})

    except Exception as e:
        # エラーが発生した場合、ログに出力しエラーメッセージを返す
        print(f"エラー発生（generate_menu）: {type(e).__name__}: {e}")
        return jsonify({"error": "献立生成に失敗しました"}), 500

# アプリケーションをデバッグモードで起動
if __name__ == "__main__":
    app.run(debug=True)