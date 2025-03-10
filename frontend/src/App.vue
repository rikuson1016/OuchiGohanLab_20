<script setup>
import { ref, onMounted } from "vue";

const ingredients = ref([]);
const newIngredient = ref("");
const menu = ref("");

// 材料を取得
const fetchIngredients = async () => {
  const response = await fetch("http://127.0.0.1:5000/ingredients");
  ingredients.value = await response.json();
};

// 材料を追加
const addIngredient = async () => {
  if (!newIngredient.value) return;

  await fetch("http://127.0.0.1:5000/ingredients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: newIngredient.value }),
  });

  newIngredient.value = "";
  fetchIngredients(); // リストを更新
};

// 材料を削除
const deleteIngredient = async (ingredientName) => {
  ingredients.value = ingredients.value.filter(i => i.name !== ingredientName);
  
  await fetch("http://127.0.0.1:5000/ingredients", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name: ingredientName }),
  });

  fetchIngredients(); // リストを更新
};

// 献立を生成
const generateMenu = async () => {
  menu.value = "献立を考えています...";

  const response = await fetch("http://127.0.0.1:5000/generate_menu", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });

  const data = await response.json();
  menu.value = data.menu;
};

// 初回ロード時にデータ取得
onMounted(fetchIngredients);
</script>

<template>
  <div class="container">
    <h1>献立アプリ</h1>
    <div class="input-section">
      <input v-model="newIngredient" placeholder="材料を入力" />
      <button class="add-button" @click="addIngredient">追加</button>
    </div>

    <h2>保存した材料</h2>
    <ul class="ingredient-list">
      <li v-for="ingredient in ingredients" :key="ingredient.name">
        {{ ingredient.name }}
        <button class="delete-button" @click="deleteIngredient(ingredient.name)">×</button>
      </li>
    </ul>

    <button class="menu-button" @click="generateMenu">献立を考える</button>

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
}

.add-button:hover, .menu-button:hover {
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
