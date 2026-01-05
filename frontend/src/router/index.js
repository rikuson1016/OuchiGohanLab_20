// src/router/index.js
import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/home.vue";
// import IngredientInput from "../components/IngredientInput.vue";
import IngredientList from "../components/IngredientList.vue";
import TodaysMenu from "../components/TodaysMenu.vue";
import Calendar from "../components/Calendar.vue";

const routes = [
    { path: "/", name: "home", component: Home },
    // { path: "/input", name: "ingredient-input", component: IngredientInput },
    { path: "/list", name: "ingredient-list", component: IngredientList },
    { path: "/today", name: "todays-menu", component: TodaysMenu },
    { path: "/calendar", name: "calendar", component: Calendar },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;