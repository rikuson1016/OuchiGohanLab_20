<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

const isLoading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

// ★人数設定用の変数★
const servings = ref(2); 

// --- 関数定義 ---

const fetchServings = async () => {
    isLoading.value = true;
    errorMessage.value = '';
    try {
        const response = await fetch(`${API_BASE}/config/servings`);
        if (!response.ok) {
            throw new Error("人数設定の取得に失敗しました");
        }
        const data = await response.json();
        servings.value = data.servings;
    } catch (error) {
        errorMessage.value = error.message;
    } finally {
        isLoading.value = false;
    }
};

const saveServings = async () => {
    successMessage.value = '';
    errorMessage.value = '';

    if (servings.value <= 0 || !Number.isInteger(servings.value)) {
        errorMessage.value = "人数は1以上の整数を入力してください。";
        return;
    }

    isLoading.value = true;
    try {
        const response = await fetch(`${API_BASE}/config/servings`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ servings: servings.value }),
        });
        
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "人数設定の保存に失敗しました");
        }
        
        successMessage.value = data.message;
        
    } catch (error) {
        errorMessage.value = error.message;
    } finally {
        isLoading.value = false;
    }
};

const goToList = () => router.push('/list');
const goToToday = () => router.push('/today');
const goToCalendar = () => router.push('/calendar'); // 材料追加もリスト画面で対応

onMounted(fetchServings); // ページ読み込み時に現在の設定をロード
</script>

<template>
  <div class="home-wrapper">
    <div class="container">
      <div class="header-section">
        <h1>おうちごはんラボ</h1>
        <p>冷蔵庫の材料で、とっておきの献立を。</p>
      </div>

      <div class="servings-setting-section">
          <h2>🍽️ 何人分の献立を提案しますか？</h2>
          <div class="input-group">
              <input 
                  type="number" 
                  v-model.number="servings" 
                  min="1" 
                  class="servings-input"
                  :disabled="isLoading"
                  @change="saveServings"
                  @keyup.enter="saveServings"
              />
              <span>人分</span>
              <button @click="saveServings" class="save-button" :disabled="isLoading">
                  {{ isLoading ? '保存中...' : '設定を保存' }}
              </button>
          </div>

          <Transition name="fade">
              <p v-if="successMessage" class="message success-message">{{ successMessage }}</p>
          </Transition>
          <Transition name="fade">
              <p v-if="errorMessage" class="message error-message">{{ errorMessage }}</p>
          </Transition>
      </div>
      <div class="card-group">
        <div class="card" @click="goToList">
          <div class="card-icon">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M19.5 3.75h-15a.75.75 0 00-.75.75V19.5a.75.75 0 00.75.75h15a.75.75 0 00.75-.75V4.5a.75.75 0 00-.75-.75zM8.25 6h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 010-1.5zM8.25 9h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 010-1.5zM8.25 12h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 010-1.5zM8.25 15h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 010-1.5zM8.25 18h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 010-1.5z" />
            </svg>
          </div>
          <div class="card-content">
            <h2>材料リスト</h2>
            <p>登録した食材を管理・確認</p>
          </div>
        </div>

        <div class="card" @click="goToToday">
          <div class="card-icon" style="background: #e9f8e8; color: #2ecc71;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 3h12a3 3 0 013 3v12a3 3 0 01-3 3H6a3 3 0 01-3-3V6a3 3 0 013-3zm1.5 6h9a.75.75 0 010 1.5h-9a.75.75 0 010-1.5zm0 3.75h9a.75.75 0 010 1.5h-9a.75.75 0 010-1.5zm0 3.75h9a.75.75 0 010 1.5h-9a.75.75 0 010-1.5z" />
            </svg>
          </div>
          <div class="card-content">
            <h2>献立を考える</h2>
            <p>AIが今日の献立を提案します</p>
          </div>
        </div>

        <div class="card" @click="goToCalendar">
          <div class="card-icon" style="background: #fdf3e8; color: #e67e22;">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
              <path d="M6 3h12a3 3 0 013 3v12a3 3 0 01-3 3H6a3 3 0 01-3-3V6a3 3 0 013-3zm1.5 3.75a.75.75 0 00-.75.75v1.5a.75.75 0 001.5 0v-1.5a.75.75 0 00-.75-.75zm0 4.5a.75.75 0 00-.75.75v1.5a.75.75 0 001.5 0v-1.5a.75.75 0 00-.75-.75zm0 4.5a.75.75 0 00-.75.75v1.5a.75.75 0 001.5 0v-1.5a.75.75 0 00-.75-.75zM12 6.75a.75.75 0 00-.75.75v1.5a.75.75 0 001.5 0v-1.5a.75.75 0 00-.75-.75zm0 4.5a.75.75 0 00-.75.75v1.5a.75.75 0 001.5 0v-1.5a.75.75 0 00-.75-.75zm0 4.5a.75.75 0 00-.75.75v1.5a.75.75 0 001.5 0v-1.5a.75.75 0 00-.75-.75zm4.5-9a.75.75 0 00-.75.75v1.5a.75.75 0 001.5 0v-1.5a.75.75 0 00-.75-.75zm0 4.5a.75.75 0 00-.75.75v1.5a.75.75 0 001.5 0v-1.5a.75.75 0 00-.75-.75zm0 4.5a.75.75 0 00-.75.75v1.5a.75.75 0 001.5 0v-1.5a.75.75 0 00-.75-.75z" />
            </svg>
          </div>
          <div class="card-content">
            <h2>献立カレンダー</h2>
            <p>これまでの献立履歴を振り返る</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* 全体的なレイアウトと背景 */
/* ... (既存のスタイルはそのまま) ... */

/* ★人数設定セクションのスタイルを追加★ */
.servings-setting-section {
    margin: 20px auto 40px; /* カードとの間にスペースを追加 */
    padding: 25px;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    background-color: #fcfcfc;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.servings-setting-section h2 {
    font-size: 1.4em;
    color: #e67e22; /* 目立つ色に変更 */
    margin-bottom: 20px;
}

.input-group {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 15px;
}

.servings-input {
    width: 70px;
    padding: 10px;
    font-size: 1.1em;
    border: 2px solid #bdc3c7;
    border-radius: 8px;
    text-align: center;
    transition: border-color 0.3s;
}
.servings-input:focus {
    border-color: #3498db;
    outline: none;
}

.save-button {
    padding: 10px 20px;
    background: #3498db; 
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-weight: bold;
    transition: background 0.3s, opacity 0.3s;
}
.save-button:hover:not(:disabled) {
    background: #2980b9;
}
.save-button:disabled {
    background: #ccc;
    cursor: not-allowed;
    opacity: 0.7;
}

.message {
    margin-top: 15px;
    padding: 10px;
    border-radius: 8px;
    font-weight: 600;
}
.success-message {
    background-color: #d4edda;
    color: #155724;
    border: 1px solid #c3e6cb;
}
.error-message {
    background-color: #f8d7da;
    color: #721c24;
    border: 1px solid #f5c6cb;
}

/* アニメーション */
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* 全体的なレイアウトと背景 */
.home-wrapper {
  background: linear-gradient(rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.7)), url('/kitchen-bg.jpg'); /* 背景画像 */
  background-size: cover;
  background-position: center;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.container {
  max-width: 900px;
  width: 100%;
  padding: 40px;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  text-align: center;
}

/* ヘッダーセクション */
.header-section {
  margin-bottom: 40px;
}

h1 {
  font-size: 3em;
  color: #2c3e50;
  margin-bottom: 10px;
  font-weight: 700;
}

p {
  font-size: 1.2em;
  color: #7f8c8d;
}

/* カードグループ */
.card-group {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 30px;
}

.card {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: #ffffff;
  border-radius: 15px;
  padding: 30px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  width: 250px;
}
.card:hover {
  transform: translateY(-8px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.12);
}

.card-icon {
  width: 60px;
  height: 60px;
  margin-bottom: 20px;
  background: #eaf6fd;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3498db;
}
.card-icon svg {
  width: 30px;
  height: 30px;
}

.card-content h2 {
  font-size: 1.5em;
  color: #34495e;
  margin-bottom: 5px;
}
.card-content p {
  font-size: 0.9em;
  color: #95a5a6;
}

/* レスポンシブデザイン */
@media (max-width: 768px) {
  .card-group {
    flex-direction: column;
  }
}
</style>