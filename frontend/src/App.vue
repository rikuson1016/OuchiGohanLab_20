<script setup>
import { ref, onMounted } from "vue";

const ingredients = ref([]);
const newIngredient = ref("");
const menu = ref("");
const isLoading = ref(false);
const errorMessage = ref("");

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000";

const fetchIngredients = async () => {
    isLoading.value = true;
    try {
        const response = await fetch(`${API_BASE}/ingredients`);
        if (!response.ok) throw new Error("データの取得に失敗しました");
        ingredients.value = await response.json();
        errorMessage.value = "";
    } catch (error) {
        errorMessage.value = error.message;
        console.error(error);
    } finally {
        isLoading.value = false;
    }
};

const addIngredient = async () => {
    if (!newIngredient.value.trim()) return;
    isLoading.value = true;
    try {
        const response = await fetch(`${API_BASE}/ingredients`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: newIngredient.value }),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "材料の追加に失敗しました");
        }
        newIngredient.value = "";
        await fetchIngredients();
        errorMessage.value = "";
    } catch (error) {
        errorMessage.value = error.message;
        console.error(error);
    } finally {
        isLoading.value = false;
    }
};

const deleteIngredient = async (ingredientName) => {
    isLoading.value = true;
    try {
        const response = await fetch(`${API_BASE}/ingredients`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: ingredientName }),
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "材料の削除に失敗しました");
        }
        await fetchIngredients();
        errorMessage.value = "";
    } catch (error) {
        errorMessage.value = error.message;
        console.error(error);
    } finally {
        isLoading.value = false;
    }
};

const generateMenu = async () => {
    menu.value = "献立を考えています...";
    isLoading.value = true;
    try {
        const response = await fetch(`${API_BASE}/generate_menu`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || "献立の生成に失敗しました");
        }
        const data = await response.json();
        menu.value = data.menu;
        errorMessage.value = "";
    } catch (error) {
        menu.value = "";
        errorMessage.value = error.message;
        console.error(error);
    } finally {
        isLoading.value = false;
    }
};

onMounted(fetchIngredients);
</script>

<template>
    <div class="container">
        <h1>献立アプリ</h1>
        <div class="input-section">
            <input v-model="newIngredient" placeholder="材料を入力" @keyup.enter="addIngredient" />
            <button class="add-button" @click="addIngredient" :disabled="isLoading || !newIngredient.trim()">
                {{ isLoading ? "追加中..." : "追加" }}
            </button>
        </div>
        <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
        <h2>保存した材料</h2>
        <ul class="ingredient-list">
            <li v-if="!ingredients.length">まだ材料がありません</li>
            <li v-else v-for="ingredient in ingredients" :key="ingredient.name">
                {{ ingredient.name }}
                <button class="delete-button" @click="deleteIngredient(ingredient.name)">×</button>
            </li>
        </ul>
        <button class="menu-button" @click="generateMenu" :disabled="isLoading || !ingredients.length">
            {{ isLoading ? "考え中..." : "献立を考える" }}
        </button>
        <button class="clear-button" @click="menu = ''" v-if="menu">献立をクリア</button>
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
  width: 150%;  /* 幅を50%に設定 */
  margin: auto;  /* 中央に配置 */
  padding: 100px;  /* 内側の余白 */
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