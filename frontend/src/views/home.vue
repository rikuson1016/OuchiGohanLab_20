```vue
<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

// ページ遷移関数
const goToInput = () => router.push("/input");
const goToList = () => router.push("/list");
const goToToday = () => router.push("/today");
</script>

<template>
    <div class="container">
        <h1>おうちごはんラボ</h1>
        <p>冷蔵庫の材料で美味しい献立を考えましょう！</p>
        <div class="button-group">
            <button class="nav-button" @click="goToInput">材料を入力</button>
            <button class="nav-button" @click="goToList">材料リストを見る</button>
            <button class="nav-button" @click="goToToday">今日の献立を見る</button>
        </div>
    </div>
</template>

<style scoped>
.container {
    max-width: 800px;
    margin: auto;
    padding: 20px;
    text-align: center;
    background: white;
    border-radius: 10px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

h1 {
    color: #333;
    font-size: 2em;
    margin-bottom: 10px;
}

p {
    color: #666;
    font-size: 1.1em;
    margin-bottom: 20px;
}

.button-group {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.nav-button {
    padding: 12px 20px;
    border: none;
    background: #007bff;
    color: white;
    font-size: 1.1em;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.3s;
}

.nav-button:hover {
    background: #0056b3;
}
</style>
```