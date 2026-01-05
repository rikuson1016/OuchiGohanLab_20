from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from datetime import datetime

# 環境変数をロード
load_dotenv()

# --- Gemini APIの初期化 ---
try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEYが設定されていません。")
    genai.configure(api_key=api_key)
    
    # ★モデル選択ロジック: 安定版を優先★
    FINAL_MODEL_NAME = "gemini-flash-latest" 
    
    available_model_names = [
        m.name for m in genai.list_models() 
        if "generateContent" in m.supported_generation_methods
    ]

    # モデルリストに意図したモデルが含まれているかを確認
    if FINAL_MODEL_NAME not in available_model_names:
        # 代替として、リストにある「models/gemini-2.5-flash」を試みる
        ALTERNATIVE_MODEL = "models/gemini-2.5-flash"
        if ALTERNATIVE_MODEL in available_model_names:
            selected_model_name = ALTERNATIVE_MODEL
        else:
            raise ValueError(f"要求されたモデル '{FINAL_MODEL_NAME}' および代替モデル '{ALTERNATIVE_MODEL}' が見つかりません。")
    else:
        selected_model_name = FINAL_MODEL_NAME
        
    model = genai.GenerativeModel(selected_model_name)
    print(f"使用しているモデル: {selected_model_name}")

except Exception as e:
    print(f"Gemini APIの初期化エラー: {e}")
    raise SystemExit("アプリケーションを終了します。API設定を確認してください。")

# --- Flaskアプリケーション設定 ---
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "DELETE", "OPTIONS"]}})

# --- ファイルパス設定 ---
DATA_FILE = "ingredients.json"
HISTORY_FILE = "menu_history.json"
CONFIG_FILE = "config.json" # ★設定ファイル追加★

# --- ファイル操作の共通関数 ---
def load_json(file_path):
    """JSONファイルからデータを読み込む"""
    try:
        if not os.path.exists(file_path):
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # print(f"ファイル読み込みエラー({file_path}): {e}")
        return []

def save_json(data, file_path):
    """データをJSONファイルに保存する"""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"ファイル保存エラー({file_path}): {e}")

# --- ★人数設定の保存・読み込み関数 (load_config, save_config) ★ ---
def load_config():
    """設定ファイルからデータを読み込む（人数設定用）"""
    try:
        if not os.path.exists(CONFIG_FILE):
            return {"servings": 2} # デフォルト値
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            # 整数型かチェック
            if not isinstance(config.get("servings"), int) or config["servings"] <= 0:
                return {"servings": 2} 
            return config
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # print(f"設定ファイル読み込みエラー({CONFIG_FILE}): {e}")
        return {"servings": 2} 

def save_config(config):
    """データを設定ファイルに保存する"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"設定ファイル保存エラー({CONFIG_FILE}): {e}")

# --- ★人数設定エンドポイントの追加★ ---
@app.route("/config/servings", methods=["GET", "POST"])
def manage_servings():
    config = load_config()
    if request.method == "GET":
        return jsonify({"servings": config["servings"]})
    
    elif request.method == "POST":
        data = request.get_json()
        new_servings = data.get("servings")
        
        if new_servings is None or not isinstance(new_servings, int) or new_servings <= 0:
            return jsonify({"error": "有効な人数（正の整数）が必要です"}), 400
        
        config["servings"] = new_servings
        save_config(config)
        return jsonify({"message": f"{new_servings}人分に設定しました", "servings": new_servings})


# --- 食材管理エンドポイントの修正（購入価格からの単価自動計算対応） ---
@app.route("/ingredients", methods=["GET", "POST", "DELETE"])
def manage_ingredients():
    try:
        ingredients = load_json(DATA_FILE)
        
        # GET および POST のロジックは省略（変更なしと仮定）
        if request.method == "GET":
            return jsonify(ingredients)
        
        elif request.method == "POST":
            # ... (POST ロジックは省略) ...
            # ★注意：POSTロジックは前回の修正（購入総額からの単価計算）を適用してください★
            
            data = request.get_json()
            ingredient_name = data.get("name")
            purchased_quantity = data.get("quantity") 
            unit = data.get("unit")
            purchased_price = data.get("purchased_price") 
            
            if not all([ingredient_name, purchased_quantity, unit, purchased_price is not None]):
                return jsonify({"error": "材料名、数量、単位、購入総額が必要です"}), 400

            if purchased_quantity <= 0:
                return jsonify({"error": "数量は正の数である必要があります"}), 400

            price_per_unit = purchased_price / purchased_quantity
            
            existing_item = next((item for item in ingredients if item['name'] == ingredient_name and item.get('unit') == unit), None)
            
            if existing_item:
                existing_item['quantity'] += purchased_quantity
                existing_item['price_per_unit'] = price_per_unit
                message = f"{ingredient_name}の数量を加算しました"
            else:
                ingredients.append({"name": ingredient_name, "quantity": purchased_quantity, "unit": unit, "price_per_unit": price_per_unit})
                message = "材料を追加しました"

            save_json(ingredients, DATA_FILE)
            return jsonify({"message": message, "ingredients": ingredients})

        
        elif request.method == "DELETE":
            data = request.get_json()
            name_to_delete = data.get("name")
            unit_to_delete = data.get("unit")
            
            # 必須チェックを強化
            if not name_to_delete or not unit_to_delete:
                return jsonify({"error": "削除する材料名と単位が必要です"}), 400

            # 削除フラグ
            initial_count = len(ingredients)
            
            # 名前と単位が一致するアイテムを削除
            ingredients = [item for item in ingredients if not (item["name"] == name_to_delete and item.get("unit") == unit_to_delete)]
            
            final_count = len(ingredients)
            
            save_json(ingredients, DATA_FILE)
            
            # 削除できたかどうかにかかわらず、必ずレスポンスを返す
            if final_count < initial_count:
                return jsonify({"message": "材料を削除しました", "ingredients": ingredients})
            else:
                # 削除対象が見つからなかった場合もエラーではなく正常レスポンスを返す
                return jsonify({"message": "削除対象の材料は見つかりませんでした", "ingredients": ingredients}), 200

    except Exception as e:
        print(f"エラー（/ingredients）: {e}")
        return jsonify({"error": "サーバーエラーが発生しました"}), 500


# --- 献立生成エンドポイントの修正（人数・数量対応） ---
@app.route("/generate_menu", methods=["POST"])
def generate_menu():
    try:
        ingredients = load_json(DATA_FILE)
        if not ingredients:
            return jsonify({"main_dish_options": []})

        config = load_config()
        servings = config.get("servings", 2)
        meal_time = request.get_json().get("meal_time", "夜")
        
        # 在庫の単価情報を辞書にマッピングして、Python側での計算に備える
        # キー: "材料名-単位" (例: "鶏むね肉-g")、値: 単価
        price_map = {
            f"{item['name']}-{item['unit']}": item.get('price_per_unit', 0)
            for item in ingredients
        }
        
        # 材料リストを数量と単価付きで整形
        ingredient_list_detailed = "\n".join([
            f"- {item['name']}: {item['quantity']}{item['unit']} (単価: {item.get('price_per_unit', 0)}円/{item['unit']})"
            for item in ingredients
        ])
        
        prompt = f"""
        あなたは、冷蔵庫にある材料から献立を提案する優秀な料理アシスタントです。
        以下の在庫材料リストとルールに従って、{servings}人分の{meal_time}の主菜候補を3つ提案してください。

        # 在庫材料リスト
        {ingredient_list_detailed}

        # ルール
        1. {servings}人分の分量を考慮し、{meal_time}に合った献立を提案すること。
        2. 提案する献立は、在庫にある**数量と単価**をなるべく多く使えるように考慮すること。
        3. 各献立は、json形式で出力すること。
        4. jsonは以下のフォーマットで出力すること。特に**price**フィールドには**0**を設定し、**ingredients_used**には、提案された献立で実際に使用する材料とその数量・単位を正確に含めること。

        # 出力フォーマット
        {{
            "main_dish_options": [
                {{
                    "name": "", 
                    "description": "", 
                    "price": 0,  // ★Python側で計算するため、常に0を出力してください★
                    "youtube_url": "https://www.youtube.com/results?search_query=献立名+作り方+人気",
                    "ingredients_used": [
                        {{"name": "鶏肉", "quantity": 300, "unit": "g"}},
                    ]
                }},
                // ... 他の2つの候補も同様の構造 ...
            ]
        }}
        """

        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if json_match:
            cleaned_text = json_match.group(0)
            try:
                menu_data = json.loads(cleaned_text)
                
                # ★★★ Python側で正確な合計価格を計算するロジック ★★★
                for dish in menu_data.get("main_dish_options", []):
                    total_price = 0
                    for used_item in dish.get("ingredients_used", []):
                        use_name = used_item.get('name')
                        use_qty = used_item.get('quantity', 0)
                        use_unit = used_item.get('unit')
                        
                        key = f"{use_name}-{use_unit}"
                        
                        # 在庫価格マップから単価を取得
                        price_per_unit = price_map.get(key, 0)
                        
                        # (使用量 * 単価) を計算し、合計に追加
                        item_cost = use_qty * price_per_unit
                        total_price += item_cost

                    # 計算した価格をpriceフィールドに設定（四捨五入して整数に）
                    dish["price"] = int(round(total_price))
                # ★★★ 価格計算ロジック終了 ★★★
        
        
                return jsonify(menu_data)

            except json.JSONDecodeError as e:
                print(f"JSONパースエラー: {e}. 元のテキスト: {cleaned_text}")

        # JSONパース失敗時のフォールバック
        fallback_options = {
            "main_dish_options": [
                {"name": "おまかせ定食", "description": "シンプルながらもバランスの取れた一品。", "price": 0, "youtube_url": "https://www.youtube.com/results?search_query=定食+レシピ", "ingredients_used": []},
            ]
        }
        return jsonify(fallback_options)
        
    except Exception as e:
        print(f"エラー（/generate_menu）: {e}")
        return jsonify({"error": f"献立生成に失敗しました: {str(e)}"}), 500


# --- 献立履歴管理エンドポイントの修正（在庫減算ロジックを追加） ---
@app.route("/menu_history", methods=["GET", "POST"])
def menu_history():
    history = load_json(HISTORY_FILE)
    if request.method == "GET":
        month = request.args.get("month")
        # ... (GETロジックは変更なし) ...
        filtered_history = [item for item in history if item.get("date", "").startswith(month)] if month else history
        total_price = sum(item.get("dish", {}).get("price", 0) for item in filtered_history)
        return jsonify({"history": filtered_history, "total_price": total_price})
    
    elif request.method == "POST":
        data = request.get_json()
        date = data.get("date")
        dish = data.get("dish") # dishには ingredients_used が含まれる
        meal_time = data.get("meal_time")
        
        if not all([date, dish, dish.get("name"), meal_time]):
            return jsonify({"error": "無効なデータです（日付、主菜、時間帯が必要）"}), 400
        
        history.append({"date": date, "dish": dish, "meal_time": meal_time})
        save_json(history, HISTORY_FILE)
        
        # ★献立を保存後、材料を在庫から減らす処理★
        if dish.get("ingredients_used"):
            current_ingredients = load_json(DATA_FILE)
            for used_item in dish["ingredients_used"]:
                use_name = used_item.get('name')
                use_qty = used_item.get('quantity', 0)
                use_unit = used_item.get('unit')
                
                # 在庫から一致する材料を探す（名前と単位が一致）
                match_index = next((i for i, item in enumerate(current_ingredients) 
                                    if item.get('name') == use_name and item.get('unit') == use_unit), -1)
                
                if match_index != -1 and use_qty > 0:
                    stock_item = current_ingredients[match_index]
                    stock_item['quantity'] -= use_qty
                    
                    # 数量が0以下になったら在庫から削除
                    if stock_item['quantity'] <= 0:
                        del current_ingredients[match_index]
            
            save_json(current_ingredients, DATA_FILE)
            
        return jsonify({"message": "献立を保存し、材料を在庫から差し引きました"})

# --- サーバー起動 ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)