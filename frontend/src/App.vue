<!-- src/App.vue -->
<script setup>
import { computed, watchEffect } from "vue";
import { useRouter, useRoute } from "vue-router";

const router = useRouter();
const route = useRoute();

const navigateTo = (path) => router.push(path);

// ルート名に基づくbodyクラスの設定
const bodyClass = computed(() => {
    switch (route.name) {
        case "home": return "home";
        // case "ingredient-input": return "ingredient-input";
        case "ingredient-list": return "ingredient-list";
        case "todays-menu": return "todays-menu";
        default: return "";
    }
});

// bodyクラスを動的に更新
watchEffect(() => {
    document.body.className = bodyClass.value;
});
</script>

<template>
    <div class="app-container">
        <!-- グローバルナビゲーション -->
        <header class="navbar">
            <h2>おうちごはんラボ</h2>
            <nav>
                <button class="nav-button" @click="navigateTo('/')">ホーム</button>
                <!-- <button class="nav-button" @click="navigateTo('/input')">材料入力</button> -->
                <button class="nav-button" @click="navigateTo('/list')">材料リスト</button>
                <button class="nav-button" @click="navigateTo('/today')">今日の献立</button>
                <button class="nav-button" @click="navigateTo('/calendar')">献立カレンダー</button>
            </nav>
        </header>
        <!-- ページコンテンツ -->
        <main>
            <router-view></router-view>
        </main>
    </div>
</template>

<style scoped>
.app-container {
    font-family: Arial, sans-serif;
    min-height: 100vh;
}

.navbar {
    background: #007bff;
    color: white;
    padding: 10px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.navbar h2 {
    margin: 0;
    font-size: 1.5em;
}

nav {
    display: flex;
    gap: 10px;
}

.nav-button {
    background: none;
    border: 1px solid white;
    color: white;
    padding: 8px 15px;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.3s;
}

.nav-button:hover {
    background: rgba(255, 255, 255, 0.2);
}

main {
    max-width: 800px;
    margin: auto;
    padding: 20px;
}
</style>
```