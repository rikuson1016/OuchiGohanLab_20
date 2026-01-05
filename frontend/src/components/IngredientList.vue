```vue
<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";


const ingredients = ref([]);
const newIngredientName = ref("");
const newIngredientQuantity = ref(1); 
const newIngredientUnit = ref("g"); 
// ★変更：1単位単価から購入総額に
const newIngredientPurchasedPrice = ref(0); 
const isLoading = ref(false);
const errorMessage = ref(""); 
const router = useRouter();

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:5000";

const fetchIngredients = async () => {
    isLoading.value = true;
    errorMessage.value = "";
    try {
        const response = await fetch(`${API_BASE}/ingredients`);
        if (!response.ok) {
            throw new Error("材料の取得に失敗しました");
        }
        const data = await response.json();
        ingredients.value = Array.isArray(data) ? data : [];
    } catch (error) {
        errorMessage.value = error.message;
    } finally {
        isLoading.value = false;
    }
};

const addIngredient = async () => {
    // ★チェックロジックを修正
    if (!newIngredientName.value.trim() || newIngredientQuantity.value <= 0 || newIngredientPurchasedPrice.value < 0) {
        errorMessage.value = "有効な材料名、数量、購入総額を入力してください。数量は1以上である必要があります";
        return;
    }
    isLoading.value = true;
    errorMessage.value = "";
    try {
        const response = await fetch(`${API_BASE}/ingredients`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: newIngredientName.value.trim(),
                quantity: newIngredientQuantity.value, // 購入数量として送信
                unit: newIngredientUnit.value,
                purchased_price: newIngredientPurchasedPrice.value, // ★購入総額として送信★
            }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "材料の追加に失敗しました");
        }
        
        // 成功したらフォームをリセット
        newIngredientName.value = "";
        newIngredientQuantity.value = 1;
        newIngredientUnit.value = "g";
        newIngredientPurchasedPrice.value = 0; // ★リセット★
        fetchIngredients(); 
    } catch (error) {
        errorMessage.value = error.message;
    } finally {
        isLoading.value = false;
    }
};


const deleteIngredient = async (ingredient) => {
    isLoading.value = true;
    errorMessage.value = "";
    try {
        const response = await fetch(`${API_BASE}/ingredients`, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ 
                name: ingredient.name,
                unit: ingredient.unit, // ★単位も指定して削除
            }),
        });
        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || "材料の削除に失敗しました");
        }
        fetchIngredients(); // リストを更新
    } catch (error) {
        errorMessage.value = error.message;
    } finally {
        isLoading.value = false;
    }
};

onMounted(fetchIngredients);
</script>

<template>
  <div class="container">
    <div class="add-form">
      <input v-model="newIngredientName" placeholder="材料名" class="input-name" />
      
      <div class="quantity-input-group">
        <input 
          type="number" 
          v-model.number="newIngredientQuantity" 
          min="1" 
          class="input-quantity"
        />
        <select v-model="newIngredientUnit" class="select-unit">
          <option value="g">g</option>
          <option value="ml">ml</option>
          <option value="個">個</option>
          <option value="パック">パック</option>
          <option value="本">本</option>
        </select>
      </div>
      
      <div class="price-input-group">
        <input 
          type="number" 
          v-model.number="newIngredientPurchasedPrice" 
          min="0" 
          class="input-price"
        />
        <span>円 (購入総額)</span>
      </div>
      <button @click="addIngredient" class="add-button">追加</button>
    </div>

    <div class="ingredient-list">
      <TransitionGroup name="list">
        <div v-for="ingredient in ingredients" :key="ingredient.name + ingredient.unit" class="ingredient-item">
          <span class="ingredient-name">
            {{ ingredient.name }}
            <span class="ingredient-quantity">
                {{ ingredient.quantity }}{{ ingredient.unit }} 
                (単価: 約{{ Math.round(ingredient.price_per_unit) }}円/{{ ingredient.unit }}) 
            </span>
          </span>
          <button @click="deleteIngredient(ingredient)" class="delete-button">削除</button>
        </div>
      </TransitionGroup>
      <p v-if="!isLoading && ingredients.length === 0" class="info-message">在庫がありません。材料を追加してください。</p>
    </div>
    
    </div>
</template>

<style scoped>
/* スタイルは簡略化しています。既存のスタイルとマージしてください。 */
.container {
    max-width: 600px;
    margin: auto;
    padding: 20px;
    text-align: center;
}

/* ★修正：フォームのレイアウト変更 */
.add-form {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    align-items: center;
}
.input-name {
    flex-grow: 1;
    padding: 10px;
}
/* ★追加：数量と単位のグループスタイル */
.quantity-input-group {
    display: flex;
    gap: 5px;
}
.input-quantity {
    width: 60px;
    padding: 10px;
    text-align: right;
}
.select-unit {
    padding: 10px;
}
.add-button {
    padding: 10px 20px;
    background: #2ecc71;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
}

.ingredient-list {
    margin-top: 20px;
}
.ingredient-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    border-bottom: 1px solid #eee;
}
/* ★追加：数量の表示スタイル */
.ingredient-name {
    font-size: 1.1em;
}
.ingredient-quantity {
    margin-left: 15px;
    font-weight: bold;
    color: #3498db;
}
.delete-button {
    background: #e74c3c;
    color: white;
    border: none;
    padding: 5px 10px;
    border-radius: 5px;
    cursor: pointer;
}


.delete-button:hover {
    background: #c82333;
}

.home-button {
    padding: 10px 20px;
    border: none;
    background: #007bff;
    color: white;
    font-size: 1em;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 10px;
    transition: background 0.3s;
}

.home-button:hover {
    background: #0056b3;
}

/* ★追加：単価入力グループのスタイル */
.price-input-group {
    display: flex;
    align-items: center;
    gap: 5px;
}
.input-price {
    width: 80px; /* 少し幅を広げる */
    padding: 10px;
    text-align: right;
}

/* ★修正：在庫表示の単価表示を調整 */
.ingredient-quantity {
    margin-left: 15px;
    font-weight: bold;
    color: #3498db;
    font-size: 0.9em;
}

</style>
```