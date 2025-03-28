<script setup>
import { ref, onMounted, computed } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const theme = ref(route.params.theme);
const questionIndex = ref(0);
const selectedAnswer = ref(null);
const showAnswer = ref(false);
const questions = ref([]);
const currentQuestion = computed(() => questions.value[questionIndex.value] || null);


const fetchQuestions = async () => {
  try {
    const response = await fetch("/questions.json");
    const data = await response.json();
    questions.value = data.questions;
    currentQuestion.value = questions.value[questionIndex.value];
  } catch (error) {
    console.error("Erreur lors du chargement des questions :", error);
    alert("Impossible de charger les questions !");
    router.push("/qcm");
  }
};

/*

const fetchQuestions = async () => {
  
    try {
    const response = await fetch("http://localhost:8000/questions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: theme.value }),
    });
    const data = await response.json();
    questions.value = data.questions;
    currentQuestion.value = questions.value[questionIndex.value];
  } catch (error) {
    console.error("Erreur lors du chargement des questions :", error);
    alert("Impossible de charger les questions !");
    router.push("/qcm");
  }
};
*/


const selectAnswer = (answerKey) => {
  if (!showAnswer.value) {
    selectedAnswer.value = answerKey;
    showAnswer.value = true;
  }
};

const nextQuestion = () => {
  if (questionIndex.value < questions.value.length - 1) {
    questionIndex.value++;
    selectedAnswer.value = null;
    showAnswer.value = false;
  } else {
    alert("QCM terminé !");
    router.push("/qcm");
  }
};

onMounted(() => {
  fetchQuestions();
});
</script>

<template>
  <div class="flex flex-col items-center justify-center h-screen w-screen bg-gray-100 p-8 relative">
    <!-- Conteneur de la question -->
    <div class="bg-white p-8 rounded-lg shadow-lg w-full flex flex-col text-left">
      <div class="flex">
        <home/>
        <h1 class="text-sm p-2 mb-4 text-left font-light">
          {{ theme }} - Question {{ questionIndex + 1 }} / {{ questions.length }}
        </h1>
      </div>
      <p class="text-2xl font-semibold mb-6">{{ currentQuestion?.question }}</p>

      <!-- Réponses sous forme de cartes -->
      <div class="grid grid-cols-2 gap-6 flex-1 items-center">
        <UCard 
          v-for="(answerText, answerKey) in currentQuestion?.options" 
          :key="answerKey" 
          class="cursor-pointer p-6 text-lg font-medium transition duration-200 h-64 flex items-center text-left"
          :class="{
            'bg-blue-500 text-white': selectedAnswer === answerKey,
            'bg-red-500 text-white': showAnswer && selectedAnswer === answerKey && answerKey !== currentQuestion.correct_answer,
            'bg-green-500 text-white': showAnswer && answerKey === currentQuestion.correct_answer,
            'hover:bg-gray-200': !showAnswer
          }"
          @click="selectAnswer(answerKey)">
          <span class="font-bold">{{ answerKey }}.</span> {{ answerText }}
        </UCard>
      </div>

      <!-- Affichage de la correction -->
      <div v-if="showAnswer" class="mt-4 p-4 bg-gray-100 rounded-lg">
        <p class="font-bold">Bonne réponse : {{ currentQuestion.correct_answer }}</p>
        <p class="text-gray-600">{{ currentQuestion.context_answer }}</p>
      </div>

      <div class="flex justify-center mt-4">
        <UButton 
          class="w-fit px-6 py-3 text-lg bg-green-500"  
          :disabled="!showAnswer" 
          @click="nextQuestion">
          Suivant
        </UButton>
      </div>
    </div>
  </div>
</template>