import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import IngredientInput from "../components/IngredientInput.vue";
import IngredientList from "../components/IngredientList.vue";
import TodaysMenu from "../components/TodaysMenu.vue";

const routes = [
    { path: "/", name: "Home", component: Home },
    { path: "/input", name: "IngredientInput", component: IngredientInput },
    { path: "/list", name: "IngredientList", component: IngredientList },
    { path: "/today", name: "TodaysMenu", component: TodaysMenu },
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

export default router;