<script setup>
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { Calendar } from "v-calendar";
import "v-calendar/style.css";

const history = ref([]);
const totalPrice = ref(0);
const selectedMonth = ref(new Date().toISOString().slice(0, 7));
const isLoading = ref(false);
const errorMessage = ref("");
const router = useRouter();

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

const validateHistoryItem = (item) => {
  if (!item || !item.date || !item.dish || !item.dish.name || !Number.isFinite(item.dish.price)) {
    console.warn("Invalid history item:", item);
    return {
      date: new Date().toISOString().slice(0, 10),
      dish: { name: "不明", price: 0 },
    };
  }
  const date = item.date.match(/^\d{4}-\d{2}-\d{2}$/) ? item.date : new Date(item.date).toISOString().slice(0, 10);
  return {
    date,
    dish: { name: item.dish.name, price: Number(item.dish.price) },
  };
};

const fetchHistory = async () => {
  isLoading.value = true;
  errorMessage.value = "";
  try {
    console.log(`Fetching history for month: ${selectedMonth.value}`);
    const response = await fetch(`${API_BASE}/menu_history?month=${selectedMonth.value}`);
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "履歴取得に失敗しました");
    }
    const data = await response.json();
    console.log("Received data:", data);
    history.value = Array.isArray(data.history) ? data.history.map(validateHistoryItem) : [];
    totalPrice.value = Number.isFinite(data.total_price) ? data.total_price : 0;
    console.log("Processed history:", history.value);
  } catch (error) {
    errorMessage.value = error.message;
    console.error("Fetch history error:", error);
  } finally {
    isLoading.value = false;
  }
};

const monthOptions = computed(() => {
  const options = [];
  const today = new Date();
  for (let i = 0; i < 3; i++) {
    const date = new Date(today.getFullYear(), today.getMonth() - i, 1);
    const value = date.toISOString().slice(0, 7);
    options.push({ value, label: value });
  }
  return options;
});

const updateMonth = () => {
  fetchHistory();
};

// 献立を日付ごとにグループ化する新しいcomputedプロパティ
const groupedHistory = computed(() => {
  return history.value.reduce((acc, item) => {
    (acc[item.date] = acc[item.date] || []).push(item.dish);
    return acc;
  }, {});
});

const calendarAttributes = computed(() => {
  return Object.keys(groupedHistory.value).map((date) => {
    const dishesForDate = groupedHistory.value[date];
    const dailyPrice = dishesForDate.reduce((sum, dish) => sum + dish.price, 0);
    const price = Math.min(Math.max(Math.floor(dailyPrice / 200) * 200, 0), 1000);
    
    const popoverLabel = dishesForDate.map(dish => `${dish.name} (¥${dish.price})`).join('\n');
    
    return {
      key: date,
      highlight: {
        class: `price-${price}`,
      },
      dates: new Date(date),
      popover: {
        label: popoverLabel,
      },
    };
  });
});

onMounted(() => {
  console.log("Calendar.vue mounted");
  fetchHistory();
});
</script>

<template>
  <div class="container">
    <div class="header-section">
      <h1>献立カレンダー</h1>
      <p>過去の献立履歴と月間合計金額を確認できます</p>
    </div>

    <div class="calendar-section">
      <!-- <div class="select-group">
        <label for="month-select">表示月:</label>
        <select v-model="selectedMonth" @change="updateMonth" class="month-select" id="month-select" name="month-select">
          <option v-for="option in monthOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div> -->

      <Transition name="fade" mode="out-in">
        <div v-if="isLoading" key="loading" class="message-section">
          <p class="loading-message">カレンダーを読み込み中...</p>
          <div class="spinner"></div>
        </div>
        <div v-else key="content">
          <Calendar :attributes="calendarAttributes" :masks="{ weekdays: 'WW' }" class="calendar" />
          
          <Transition name="fade">
            <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
          </Transition>
          <Transition name="fade">
            <p v-if="!history.length && !errorMessage" class="info-message">
              {{ selectedMonth }}の履歴がありません。
            </p>
          </Transition>
          <Transition name="fade">
            <p v-if="history.length" class="total-price-message">
              月間合計金額: <span class="price-value">{{ totalPrice }}円</span>
            </p>
          </Transition>
        </div>
      </Transition>
    </div>

    <div class="navigation-buttons">
      <button class="home-button" @click="router.push('/')">ホーム</button>
      <button class="today-button" @click="router.push('/today')">主菜を選ぶ</button>
      <button class="list-button" @click="router.push('/list')">材料リスト</button>
    </div>
  </div>
</template>

<style scoped>
/* 全体的なコンテナ */
.container {
  max-width: 900px;
  margin: auto;
  padding: 40px;
  text-align: center;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  font-family: 'Helvetica Neue', Arial, sans-serif;
  color: #333;
}

/* ヘッダーセクション */
.header-section {
  margin-bottom: 30px;
}
h1 {
  font-size: 2.5em;
  color: #2c3e50;
  margin-bottom: 10px;
  font-weight: 700;
}
p {
  font-size: 1.1em;
  color: #7f8c8d;
}

/* 月選択とカレンダー */
.calendar-section {
  margin-bottom: 30px;
}
.select-group {
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}
.month-select {
  padding: 10px 15px;
  border-radius: 25px;
  border: 1px solid #ddd;
  font-size: 1em;
  background: #f8f9fa;
  cursor: pointer;
  transition: all 0.3s ease;
}
.month-select:hover {
  border-color: #3498db;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.calendar {
  border-radius: 15px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  border: none;
}

/* メッセージとスピナー */
.message-section {
  min-height: 150px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}
.loading-message {
  color: #3498db;
  font-weight: bold;
}
.error-message {
  color: #e74c3c;
  font-weight: bold;
  margin-top: 15px;
}
.info-message {
  color: #95a5a6;
  font-style: italic;
  margin-top: 15px;
}
.total-price-message {
  font-size: 1.2em;
  color: #34495e;
  font-weight: 500;
  margin-top: 25px;
}
.price-value {
  color: #2ecc71;
  font-size: 1.4em;
  font-weight: bold;
}

/* ナビゲーションボタン */
.navigation-buttons {
  margin-top: 40px;
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 15px;
}
.navigation-buttons button {
  padding: 12px 25px;
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

/* 価格に応じた色変化 */
.vc-day .price-0 { background-color: #e6f3e6 !important; }
.vc-day .price-200 { background-color: #c1e0c1 !important; }
.vc-day .price-400 { background-color: #9ccc9c !important; }
.vc-day .price-600 { background-color: #78b978 !important; }
.vc-day .price-800 { background-color: #54a654 !important; }
.vc-day .price-1000 { background-color: #4caf50 !important; }
</style>