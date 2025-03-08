<script setup>
import { ref, onMounted } from "vue";

const ingredients = ref([]);
const newIngredient = ref("");

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

// 初回ロード時にデータ取得
onMounted(fetchIngredients);
</script>

<template>
  <div>
    <h1>献立アプリ</h1>
    <input v-model="newIngredient" placeholder="材料を入力" />
    <button @click="addIngredient">追加</button>

    <h2>保存した材料</h2>
    <ul>
      <li v-for="ingredient in ingredients" :key="ingredient.name">
        {{ ingredient.name }}
      </li>
    </ul>
  </div>
</template>

<style>
body {
  font-family: Arial, sans-serif;
  text-align: center;
}
input {
  margin-right: 10px;
}
</style>
