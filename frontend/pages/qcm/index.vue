<script setup lang="ts">

import { ref } from "vue";
import { useRouter } from "vue-router";
import home from "~/components/home.vue";

const router = useRouter();
const items = ref(['Math', 'Histoire', 'Science', 'Informatique'])


const selectedTheme = ref("");
const customTheme = ref("");

const startQCM = () => {
  if (selectedTheme.value) {
    router.push(`/qcm/${selectedTheme.value}`);
  } else if (customTheme.value.trim()) {
    router.push(`/qcm/${customTheme.value.trim()}`);
  }
};
</script>

<template>
<div class="flex flex-col items-center justify-center min-h-screen p-4 bg-gray-100">
   <home />
    <h1 class="text-2xl font-bold mb-4">Choisissez un thème</h1>
  <USelect v-model="selectedTheme" size="xl" :items="items" class="w-full max-w-md mb-4" placeholder="Sélectionner un thème..."/>

  <UInput 
      v-model="customTheme" 
      placeholder="Thème personnalisé..." 
      class="w-full max-w-md mb-4" 
    />
    <!-- Bouton pour commencer le QCM -->
    <UButton 
      class="max-w-md bg-green-500"  
      :disabled="!selectedTheme && !customTheme.trim()" 
      @click="startQCM">
      Commencer
    </UButton>
  </div>
</template>
