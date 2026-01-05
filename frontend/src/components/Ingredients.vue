<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const ingredients = ref([]);
const selectedDate = ref(new Date().toISOString().slice(0, 10)); // 例: 2025-08-13
const isLoading = ref(false);
const errorMessage = ref("");
const router = useRouter();

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

const fetchIngredients = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    console.log(`Fetching ingredients for date: ${selectedDate.value}`);
    // ここを /menu_history に変更し、日付と時間帯でフィルタリングするようにする
    const response = await fetch(`${API_BASE}/menu_history?date=${selectedDate.value}`);
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "材料取得に失敗しました");
    }
    const data = await response.json();
    console.log("Received data:", data);

    const allIngredients = data.history
      .filter(item => item.date === selectedDate.value)
      .flatMap(item => item.dish.ingredients); // dish.ingredientsが存在する場合を想定

    ingredients.value = Array.isArray(allIngredients) ? allIngredients : [];
  } catch (error) {
    errorMessage.value = error.message;
    console.error("Fetch ingredients error:", error);
  } finally {
    isLoading.value = false;
  }
};

const updateDate = () => {
  fetchIngredients();
};

onMounted(() => {
  console.log("Ingredients.vue mounted");
  fetchIngredients();
});
</script>

<template>
  <div class="container">
    <h1>材料リスト</h1>
    <p>献立に使う材料を確認できます</p>

    <div class="date-picker-group">
      <label for="date-select">日付を選択:</label>
      <input type="date" id="date-select" v-model="selectedDate" @change="updateDate" class="date-input" />
    </div>

    <div class="message-section">
      <Transition name="fade">
        <div v-if="isLoading" class="loading-message">
          <p>読み込み中...</p>
          <div class="spinner"></div>
        </div>
      </Transition>
      <Transition name="fade">
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </Transition>
    </div>

    <div class="ingredients-section">
      <Transition name="fade">
        <div v-if="ingredients.length" class="ingredients-card-group">
          <div v-for="(item, index) in ingredients" :key="index" class="ingredient-card">
            {{ item }}
          </div>
        </div>
      </Transition>
      <Transition name="fade">
        <p v-if="!isLoading && ingredients.length === 0" class="info-message">
          {{ selectedDate }}の献立材料は登録されていません。
        </p>
      </Transition>
    </div>

    <div class="navigation-buttons">
      <button class="home-button" @click="router.push('/')">ホームに戻る</button>
      <button class="today-button" @click="router.push('/today')">主菜を選ぶ</button>
      <button class="calendar-button" @click="router.push('/calendar')">カレンダー</button>
    </div>
  </div>
</template>

<style scoped>
/* 全体的なスタイル */
.container {
  max-width: 800px;
  margin: auto;
  padding: 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 10px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
  font-family: 'Helvetica Neue', Arial, sans-serif;
  color: #333;
}

h1 {
  font-size: 2.2em;
  color: #2c3e50;
  margin-bottom: 5px;
}

p {
  font-size: 1em;
  color: #7f8c8d;
}

.message-section {
  min-height: 50px;
}

.loading-message {
  margin: 15px 0;
  color: #3498db;
  font-weight: bold;
}

.error-message {
  color: #e74c3c;
  margin: 15px 0;
  font-weight: bold;
}

.info-message {
  margin: 15px 0;
  color: #95a5a6;
}

/* 日付ピッカー */
.date-picker-group {
  margin-bottom: 20px;
}
.date-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 1em;
  margin-left: 10px;
}

/* 材料カードのスタイル */
.ingredients-section {
  margin-top: 20px;
}
.ingredients-card-group {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 15px;
}
.ingredient-card {
  background: #fff;
  border: 1px solid #bdc3c7;
  border-radius: 10px;
  padding: 15px 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  font-size: 1.1em;
  color: #34495e;
}
.ingredient-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

/* ナビゲーションボタン */
.navigation-buttons {
  margin-top: 40px;
  display: flex;
  justify-content: center;
  gap: 15px;
}
.navigation-buttons button {
  padding: 10px 20px;
  border: none;
  background: #3498db;
  color: white;
  border-radius: 50px;
  cursor: pointer;
  transition: background 0.3s ease, transform 0.2s ease;
}
.navigation-buttons button:hover {
  background: #2980b9;
  transform: translateY(-2px);
}

/* アニメーション */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

/* スピナー */
.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top-color: #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 10px auto;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>