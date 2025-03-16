<script setup>
import { ref, onMounted } from "vue";

const ingredients = ref([]);
const newIngredient = ref("");
const menu = ref("");
const isLoading = ref(false);

// APIのベースURL
const API_BASE = "http://127.0.0.1:5000";

// 材料を取得
const fetchIngredients = async () => {
  try {
    const response = await fetch(`${API_BASE}/ingredients`);
    if (!response.ok) throw new Error("データの取得に失敗しました");
    ingredients.value = await response.json();
  } catch (error) {
    console.error(error);
  }
};

// 材料を追加
const addIngredient = async () => {
  if (!newIngredient.value.trim()) return;

  try {
    const response = await fetch(`${API_BASE}/ingredients`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newIngredient.value }),
    });
    if (!response.ok) throw new Error("材料の追加に失敗しました");

    newIngredient.value = "";
    await fetchIngredients();
  } catch (error) {
    console.error(error);
  }
};

// 材料を削除
const deleteIngredient = async (ingredientName) => {
  try {
    ingredients.value = ingredients.value.filter(i => i.name !== ingredientName);
    const response = await fetch(`${API_BASE}/ingredients`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: ingredientName }),
    });
    if (!response.ok) throw new Error("材料の削除に失敗しました");

    await fetchIngredients();
  } catch (error) {
    console.error(error);
  }
};

// 献立を生成
const generateMenu = async () => {
  menu.value = "献立を考えています...";
  isLoading.value = true;

  try {
    const response = await fetch(`${API_BASE}/generate_menu`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });
    if (!response.ok) throw new Error("献立の生成に失敗しました");

    const data = await response.json();
    menu.value = data.menu;
  } catch (error) {
    menu.value = "献立の生成に失敗しました";
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

// 初回ロード時にデータ取得
onMounted(fetchIngredients);
</script>

<template>
  <div class="container">
    <h1>献立アプリ</h1>

    <div class="input-section">
      <input v-model="newIngredient" placeholder="材料を入力" />
      <button class="add-button" @click="addIngredient" :disabled="!newIngredient.trim()">追加</button>
    </div>

    <h2>保存した材料</h2>
    <ul class="ingredient-list">
      <li v-for="ingredient in ingredients" :key="ingredient.name">
        {{ ingredient.name }}
        <button class="delete-button" @click="deleteIngredient(ingredient.name)">×</button>
      </li>
    </ul>

    <button class="menu-button" @click="generateMenu" :disabled="isLoading">
      {{ isLoading ? "考え中..." : "献立を考える" }}
    </button>

    <h2>AIが考えた献立</h2>
    <div class="menu-box">{{ menu }}</div>
  </div>
</template>

<style>
body {
  font-family: Arial, sans-serif;
  text-align: center;
  background-color: #f9f9f9;
}

.container {
  width: 50%;
  margin: auto;
  padding: 20px;
  background: white;
  box-shadow: 0px 0px 10px rgba(0, 0, 0, 0.1);
  border-radius: 10px;
}

.input-section {
  margin-bottom: 15px;
}

input {
  padding: 10px;
  width: 60%;
  border: 1px solid #ccc;
  border-radius: 5px;
  margin-right: 10px;
}

.add-button, .menu-button {
  padding: 10px 15px;
  border: none;
  background: #28a745;
  color: white;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.add-button:disabled, .menu-button:disabled {
  background: #a9a9a9;
  cursor: not-allowed;
}

.add-button:hover:not(:disabled), .menu-button:hover:not(:disabled) {
  background: #218838;
}

.ingredient-list {
  list-style: none;
  padding: 0;
}

.ingredient-list li {
  display: flex;
  justify-content: space-between;
  background: #eee;
  padding: 8px;
  border-radius: 5px;
  margin: 5px 0;
}

.delete-button {
  background: red;
  border: none;
  color: white;
  padding: 5px;
  border-radius: 5px;
  cursor: pointer;
  transition: background 0.3s;
}

.delete-button:hover {
  background: darkred;
}

.menu-box {
  background: #ffffe0;
  padding: 15px;
  border-radius: 5px;
  margin-top: 10px;
  font-size: 1.1em;
}
</style>
