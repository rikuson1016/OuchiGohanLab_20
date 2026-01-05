<!-- <script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const ingredientName = ref("");
const errorMessage = ref("");
const successMessage = ref("");
const isLoading = ref(false); // 新しくローディング状態を追加
const router = useRouter();

const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:5000";

const addIngredient = async () => {
  if (!ingredientName.value.trim()) {
    errorMessage.value = "材料名を入力してください";
    successMessage.value = "";
    return;
  }

  isLoading.value = true;
  errorMessage.value = "";
  successMessage.value = "";

  try {
    const response = await fetch(`${API_BASE}/ingredients`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: ingredientName.value.trim() }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "材料の追加に失敗しました");
    }

    const data = await response.json();
    successMessage.value = data.message;
    ingredientName.value = "";
  } catch (error) {
    errorMessage.value = error.message;
    console.error(error);
  } finally {
    isLoading.value = false;
  }
};

const goHome = () => router.push("/");
const goToList = () => router.push("/list");
</script>

<template>
  <div class="container">
    <div class="header-section">
      <h1>材料を入力</h1>
      <p>冷蔵庫にある材料を登録して、献立を提案してもらいましょう。</p>
    </div>

    <div class="input-section">
      <div class="input-group">
        <input v-model="ingredientName" type="text" placeholder="例: トマト" @keyup.enter="addIngredient" :disabled="isLoading" />
        <button class="add-button" @click="addIngredient" :disabled="isLoading">
          <span v-if="isLoading">追加中...</span>
          <span v-else>追加</span>
        </button>
      </div>

      <div class="message-section">
        <Transition name="fade">
          <div v-if="errorMessage" class="message error-message">
            <p>{{ errorMessage }}</p>
          </div>
        </Transition>
        <Transition name="fade">
          <div v-if="successMessage" class="message success-message">
            <p>{{ successMessage }}</p>
          </div>
        </Transition>
      </div>
    </div>
    
    <div class="navigation-buttons">
      <button class="home-button" @click="goHome">ホームに戻る</button>
      <button class="list-button" @click="goToList">材料リストを見る</button>
    </div>
  </div>
</template>

<style scoped>
/* 全体的なコンテナ */
.container {
  max-width: 600px;
  margin: auto;
  padding: 40px;
  text-align: center;
  background: #ffffff;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  font-family: 'Helvetica Neue', Arial, sans-serif;
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

/* 入力セクション */
.input-section {
  margin-bottom: 20px;
}

.input-group {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-bottom: 20px;
}

input {
  padding: 12px 15px;
  font-size: 1em;
  border: 1px solid #bdc3c7;
  border-radius: 50px;
  width: 250px;
  transition: all 0.3s ease;
}
input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

.add-button {
  padding: 12px 25px;
  border: none;
  background: #2ecc71;
  color: white;
  font-size: 1.1em;
  font-weight: bold;
  border-radius: 50px;
  cursor: pointer;
  transition: all 0.3s ease;
}
.add-button:hover:not(:disabled) {
  background: #27ae60;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(46, 204, 113, 0.3);
}
.add-button:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

/* メッセージ表示 */
.message-section {
  min-height: 30px;
}
.message {
  padding: 10px;
  border-radius: 5px;
  font-weight: bold;
}
.error-message {
  color: #c0392b;
  background: #fde8e7;
}
.success-message {
  color: #27ae60;
  background: #eaf8f0;
}

/* ナビゲーションボタン */
.navigation-buttons {
  margin-top: 30px;
  display: flex;
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
  transition: all 0.3s ease;
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
</style> -->