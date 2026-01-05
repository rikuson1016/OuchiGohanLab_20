<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";

const dishes = ref([]);
const selectedDish = ref(null);
const selectedMealTime = ref("昼");
const isLoading = ref(false);
const errorMessage = ref("");
const router = useRouter();

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

const fetchDishes = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    console.log("Fetching AI-generated dishes from /generate_menu");
    const response = await fetch(`${API_BASE}/generate_menu`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        meal_time: selectedMealTime.value
      }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "主菜取得に失敗しました");
    }
    const data = await response.json();
    console.log("Received dishes:", data);
    dishes.value = Array.isArray(data.main_dish_options) ? data.main_dish_options : [];
    selectedDish.value = null;
  } catch (error) {
    errorMessage.value = error.message;
    console.error("Fetch dishes error:", error);
  } finally {
    isLoading.value = false;
  }
};

const selectDish = (dish) => {
  selectedDish.value = dish;
  console.log("Selected dish:", selectedDish.value);
};

const selectMealTime = (time) => {
  selectedMealTime.value = time;
  selectedDish.value = null;
  fetchDishes();
};

const addToCalendar = async () => {
  if (!selectedDish.value) {
    errorMessage.value = "主菜を選択してください";
    return;
  }
  isLoading.value = true;
  errorMessage.value = "";
  try {
    const response = await fetch(`${API_BASE}/menu_history`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        date: new Date().toISOString().slice(0, 10),
        // ★修正なし：selectedDish全体を送信することで、
        // AIが生成した ingredients_used も含まれる
        dish: selectedDish.value, 
        meal_time: selectedMealTime.value,
      }),
    });
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "追加に失敗しました");
    }
    
    // ... (成功時のログとメッセージはそのまま) ...
    console.log("Added to calendar:", selectedDish.value.name, "for", selectedMealTime.value);
    
    // ★在庫が減った後に、献立リストを再取得する
    await fetchDishes(); 
  } catch (error) {
    errorMessage.value = error.message;
    console.error("Add to calendar error:", error);
  } finally {
    isLoading.value = false;
  }
};

onMounted(() => {
  console.log("TodaysMenu.vue mounted");
  fetchDishes();
});
</script>

<template>
  <div class="container">
    <h1>主菜を選ぶ</h1>
    <p>今日の主菜を選択してください</p>

    <div class="meal-time-group">
      <button @click="selectMealTime('朝')" :class="{ 'selected-time': selectedMealTime === '朝' }">朝</button>
      <button @click="selectMealTime('昼')" :class="{ 'selected-time': selectedMealTime === '昼' }">昼</button>
      <button @click="selectMealTime('夜')" :class="{ 'selected-time': selectedMealTime === '夜' }">夜</button>
    </div>

    <div class="message-section">
      <Transition name="fade">
        <div v-if="isLoading" class="loading-message">
          <p>AIが献立を考え中...</p>
          <div class="spinner"></div>
        </div>
      </Transition>
      <Transition name="fade">
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </Transition>
    </div>

     <Transition name="fade">
      <div v-if="dishes.length" class="dish-options">
        <div class="dish-card" v-for="dish in dishes" :key="dish.name" @click="selectDish(dish)" :class="{ selected: selectedDish?.name === dish.name }">
          <h3>{{ dish.name }}</h3>
          <p class="dish-description">{{ dish.description }}</p>
          <p class="dish-price">¥{{ dish.price }}</p>
          
          <div v-if="dish.ingredients_used && dish.ingredients_used.length" class="used-ingredients-list">
              <strong>[使用材料]</strong>
              <span v-for="(ing, index) in dish.ingredients_used" :key="index">
                  {{ ing.name }} ({{ ing.quantity }}{{ ing.unit }}){{ index < dish.ingredients_used.length - 1 ? ', ' : '' }}
              </span>
          </div>

          <a v-if="dish.youtube_url" :href="dish.youtube_url" target="_blank" rel="noopener noreferrer">
            </a>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <p v-if="!isLoading && !errorMessage && dishes.length === 0" class="info-message">主菜がありません。材料を登録してください。</p>
    </Transition>

    <div class="selected-dish-section" v-if="selectedDish">
      <h4>選択中の献立（{{ selectedMealTime }}）</h4>
      <p>{{ selectedDish.name }} (¥{{ selectedDish.price }})</p>
      <button class="add-button" @click="addToCalendar">カレンダーに追加</button>
    </div>

    <div class="navigation-buttons">
      <button class="home-button" @click="router.push('/')">ホームに戻る</button>
      <button class="list-button" @click="router.push('/list')">材料</button>
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
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
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

.meal-time-group {
  margin-bottom: 20px;
}
.meal-time-group button {
  padding: 10px 20px;
  border: 1px solid #bdc3c7;
  background: #ecf0f1;
  color: #34495e;
  cursor: pointer;
  margin: 0 5px;
  border-radius: 25px;
  transition: all 0.3s ease;
}
.meal-time-group button:hover {
  background: #dfe6e9;
}
.meal-time-group button.selected-time {
  background: #3498db;
  color: white;
  border-color: #3498db;
  box-shadow: 0 2px 5px rgba(52, 152, 219, 0.4);
}

.dish-options {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}
.dish-card {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 15px;
  padding: 20px;
  width: 200px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.dish-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}
.dish-card.selected {
  border-color: #3498db;
  background: #eaf6fd;
}
.dish-card h3 {
  font-size: 1.2em;
  margin-bottom: 5px;
  color: #2c3e50;
}
.dish-description {
  font-size: 0.9em;
  color: #7f8c8d;
}
.dish-price {
  font-size: 1.1em;
  font-weight: bold;
  color: #2ecc71;
  margin-top: 10px;
}

.selected-dish-section {
  margin-top: 30px;
  padding: 20px;
  border-top: 1px solid #ecf0f1;
}
.add-button {
  padding: 12px 25px;
  border: none;
  background: #2ecc71;
  color: white;
  border-radius: 50px;
  cursor: pointer;
  margin-top: 15px;
  font-size: 1em;
  font-weight: bold;
  transition: background 0.3s ease, transform 0.2s ease;
}
.add-button:hover {
  background: #27ae60;
  transform: translateY(-2px);
}

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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s ease, transform 0.5s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-top-color: #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 10px auto;
}
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.youtube-button {
  padding: 8px 15px;
  border: none;
  background-color: #ff0000;
  color: white;
  border-radius: 50px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 10px;
  transition: background-color 0.3s ease;
}
.youtube-button:hover {
  background-color: #cc0000;
}
.youtube-icon {
  width: 20px;
  height: 20px;
  margin-right: 5px;
}

.used-ingredients-list {
    font-size: 0.8em;
    color: #555;
    margin-top: 10px;
    padding-top: 5px;
    border-top: 1px dashed #ddd;
    text-align: left;
}

</style>