<script setup>
// Vueの機能（refとonMounted）をインポート
import { ref, onMounted } from "vue";

// 状態を管理するリアクティブ変数を定義
const ingredients = ref([]);  // 食材リスト
const newIngredient = ref("");  // 新しい食材の入力値
const menu = ref("");  // 生成された献立
const isLoading = ref(false);  // ローディング状態
const errorMessage = ref("");  // エラーメッセージ

// APIのベースURL（環境変数から取得、デフォルトはローカル開発用）
const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000";

// 食材リストを取得する関数
const fetchIngredients = async () => {
  try {
    // APIから食材データを取得
    const response = await fetch(`${API_BASE}/ingredients`);
    // レスポンスが正常でない場合エラーを投げる
    if (!response.ok) throw new Error("データの取得に失敗しました");
    // 取得したデータをingredientsに格納
    ingredients.value = await response.json();
    // 成功したらエラーメッセージをクリア
    errorMessage.value = "";
  } catch (error) {
    // エラーメッセージを設定しログに出力
    errorMessage.value = error.message;
    console.error(error);
  }
};

// 新しい食材を追加する関数
const addIngredient = async () => {
  // 入力が空の場合は何もしない
  if (!newIngredient.value.trim()) return;
  // ローディング状態を開始
  isLoading.value = true;

  try {
    // APIにPOSTリクエストを送信して食材を追加
    const response = await fetch(`${API_BASE}/ingredients`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newIngredient.value }),
    });
    // レスポンスが正常でない場合エラーを投げる
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "材料の追加に失敗しました");
    }
    // 入力欄をクリア
    newIngredient.value = "";
    // 最新の食材リストを取得
    await fetchIngredients();
    // エラーメッセージをクリア
    errorMessage.value = "";
  } catch (error) {
    // エラーメッセージを設定しログに出力
    errorMessage.value = error.message;
    console.error(error);
  } finally {
    // ローディング状態を終了
    isLoading.value = false;
  }
};

// 食材を削除する関数
const deleteIngredient = async (ingredientName) => {
  // ローディング状態を開始
  isLoading.value = true;

  try {
    // APIにDELETEリクエストを送信して食材を削除
    const response = await fetch(`${API_BASE}/ingredients`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: ingredientName }),
    });
    // レスポンスが正常でない場合エラーを投げる
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "材料の削除に失敗しました");
    }
    // 最新の食材リストを取得
    await fetchIngredients();
    // エラーメッセージをクリア
    errorMessage.value = "";
  } catch (error) {
    // エラーメッセージを設定しログに出力
    errorMessage.value = error.message;
    console.error(error);
  } finally {
    // ローディング状態を終了
    isLoading.value = false;
  }
};

// 献立を生成する関数
const generateMenu = async () => {
  // 初期メッセージを表示
  menu.value = "献立を考えています...";
  // ローディング状態を開始
  isLoading.value = true;

  try {
    // APIにPOSTリクエストを送信して献立を生成
    const response = await fetch(`${API_BASE}/generate_menu`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    // レスポンスが正常でない場合エラーを投げる
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "献立の生成に失敗しました");
    }
    // レスポンスから献立を取得して表示
    const data = await response.json();
    menu.value = data.menu;
    // エラーメッセージをクリア
    errorMessage.value = "";
  } catch (error) {
    // エラーが発生した場合、献立をクリアしてエラーメッセージを設定
    menu.value = "";
    errorMessage.value = error.message;
    console.error(error);
  } finally {
    // ローディング状態を終了
    isLoading.value = false;
  }
};

// コンポーネントがマウントされたときに食材リストを取得
onMounted(fetchIngredients);
</script>

<template>
  <!-- 全体のコンテナ -->
  <div class="container">
    <!-- アプリのタイトル -->
    <h1>献立アプリ</h1>

    <!-- 食材入力エリア -->
    <div class="input-section">
      <!-- 食材名入力欄（Enterキーでも追加可能） -->
      <input v-model="newIngredient" placeholder="材料を入力" @keyup.enter="addIngredient" />
      <!-- 追加ボタン（ローディング中や入力が空の場合は無効） -->
      <button class="add-button" @click="addIngredient" :disabled="isLoading || !newIngredient.trim()">
        {{ isLoading ? "追加中..." : "追加" }}
      </button>
    </div>

    <!-- エラーメッセージの表示（エラーがある場合のみ） -->
    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <!-- 食材リストのセクション -->
    <h2>保存した材料</h2>
    <ul class="ingredient-list">
      <!-- 食材が空の場合のメッセージ -->
      <li v-if="!ingredients.length">まだ材料がありません</li>
      <!-- 食材リストの表示（各アイテムに削除ボタン付き） -->
      <li v-else v-for="ingredient in ingredients" :key="ingredient.name">
        {{ ingredient.name }}
        <button class="delete-button" @click="deleteIngredient(ingredient.name)">×</button>
      </li>
    </ul>

    <!-- 献立生成ボタン（ローディング中や食材が空の場合は無効） -->
    <button class="menu-button" @click="generateMenu" :disabled="isLoading || !ingredients.length">
      {{ isLoading ? "考え中..." : "献立を考える" }}
    </button>
    <!-- 献立クリアボタン（献立がある場合のみ表示） -->
    <button class="clear-button" @click="menu = ''" v-if="menu">献立をクリア</button>

    <!-- 生成された献立のセクション -->
    <h2>AIが考えた献立</h2>
    <div class="menu-box">{{ menu }}</div>
  </div>
</template>

<style>
/* ページ全体のスタイル */
body {
  font-family: Arial, sans-serif;  /* フォントを指定 */
  text-align: center;  /* 中央揃え */
  background-color: #f9f9f9;  /* 背景色 */
}

/* コンテナのスタイル */
.container {
  width: 50%;  /* 幅を50%に設定 */
  margin: auto;  /* 中央に配置 */
  padding: 20px;  /* 内側の余白 */
  background: white;  /* 背景色 */
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);  /* 影を追加 */
  border-radius: 10px;  /* 角を丸く */
}

/* 入力エリアのスタイル */
.input-section {
  margin-bottom: 15px;  /* 下に余白 */
}

/* 入力欄のスタイル */
input {
  padding: 10px;  /* 内側の余白 */
  width: 60%;  /* 幅を60%に設定 */
  border: 1px solid #ccc;  /* 枠線 */
  border-radius: 5px;  /* 角を丸く */
  margin-right: 10px;  /* 右に余白 */
}

/* ボタンの共通スタイル（追加と献立生成用） */
.add-button, .menu-button {
  padding: 10px 15px;  /* 内側の余白 */
  border: none;  /* 枠線なし */
  background: #28a745;  /* 背景色（緑） */
  color: white;  /* 文字色 */
  border-radius: 5px;  /* 角を丸く */
  cursor: pointer;  /* カーソルをポインタに */
  transition: background 0.3s;  /* 背景色の変化をアニメーション */
}

/* ボタンが無効化された時のスタイル */
.add-button:disabled, .menu-button:disabled {
  background: #a9a9a9;  /* グレー */
  cursor: not-allowed;  /* カーソルを禁止マークに */
}

/* ボタンのホバー時のスタイル（無効化されていない場合のみ） */
.add-button:hover:not(:disabled), .menu-button:hover:not(:disabled) {
  background: #218838;  /* 少し暗い緑 */
}

/* 食材リストのスタイル */
.ingredient-list {
  list-style: none;  /* リストの点を削除 */
  padding: 0;  /* 内側の余白をゼロに */
}

/* 各食材アイテムのスタイル */
.ingredient-list li {
  display: flex;  /* フレックスボックスで配置 */
  justify-content: space-between;  /* 両端に配置 */
  background: #eee;  /* 背景色 */
  padding: 8px;  /* 内側の余白 */
  border-radius: 5px;  /* 角を丸く */
  margin: 5px 0;  /* 上下に余白 */
}

/* 削除ボタンのスタイル */
.delete-button {
  background: red;  /* 背景色（赤） */
  border: none;  /* 枠線なし */
  color: white;  /* 文字色 */
  padding: 5px;  /* 内側の余白 */
  border-radius: 5px;  /* 角を丸く */
  cursor: pointer;  /* カーソルをポインタに */
  transition: background 0.3s;  /* 背景色の変化をアニメーション */
}

/* 削除ボタンのホバー時のスタイル */
.delete-button:hover {
  background: darkred;  /* 少し暗い赤 */
}

/* 献立表示ボックスのスタイル */
.menu-box {
  background: #ffffe0;  /* 薄い黄色 */
  padding: 15px;  /* 内側の余白 */
  border-radius: 5px;  /* 角を丸く */
  margin-top: 10px;  /* 上に余白 */
  font-size: 1.1em;  /* フォントサイズを少し大きく */
}

/* エラーメッセージのスタイル */
.error-message {
  color: red;  /* 赤文字 */
  margin-bottom: 15px;  /* 下に余白 */
}

/* クリアボタンのスタイル */
.clear-button {
  padding: 10px 15px;  /* 内側の余白 */
  border: none;  /* 枠線なし */
  background: #dc3545;  /* 背景色（赤） */
  color: white;  /* 文字色 */
  border-radius: 5px;  /* 角を丸く */
  cursor: pointer;  /* カーソルをポインタに */
  margin-left: 10px;  /* 左に余白 */
}

/* クリアボタンのホバー時のスタイル */
.clear-button:hover {
  background: #c82333;  /* 少し暗い赤 */
}
</style>