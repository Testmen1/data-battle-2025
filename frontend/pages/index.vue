<script setup>
import { useRouter } from "vue-router";
import { ref } from "vue";

const router = useRouter();
const loading = ref(false);
const chatHistory = ref([]);


const createNewChat = async () => {
  try {
    console.log("Création d'un nouveau chat...");
    const title = `Discussion 1`;
    const res = await fetch("http://localhost:5000/chats/new", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title })
    });
    const newChat = await res.json();
    chatHistory.value.unshift(newChat);
    router.push(`/chat/${newChat._id}`);
  } catch (error) {
    console.error("Erreur lors de la création du chat :", error);
  }
};

const goToLatestChat = async () => {
  loading.value = true;
  try {
    const res = await fetch("http://localhost:5000/chats/latest");
    const data = await res.json();

    if (data && data._id) {
      router.push(`/chat/${data._id}`);
    } else {
      console.warn("Aucun chat trouvé, redirection vers un nouveau chat.");
      createNewChat();
    }

  } catch (error) {
    console.error("Erreur lors de la récupération du dernier chat :", error);
    createNewChat();
  } finally {
    loading.value = false;
  }
};

const goToQCM = () => {
  router.push("/qcm");
};
</script>

<template>
  <div class="flex items-center justify-center h-screen bg-cover bg-center">
    <div class="bg-white p-6 rounded-lg shadow-lg text-center space-y-6">
      <img src="../assets/img/onizuka1.png" alt="OnizukAI" class="w-96 mx-auto" />
      <h1 class="text-2xl text-gray-600 font-bold">Bienvenue sur OnizukAI</h1>
      <p class="text-gray-600">Choisissez une option :</p>
      <div class="space-y-4">
        <UButton color="blue" class="w-full hover:bg-blue-700 text-gray-400 cursor-pointer" :loading="loading" @click="goToLatestChat">💬 Accéder au Chatbot</UButton>
        <UButton color="green" class="w-full hover:bg-green-700 text-gray-400 cursor-pointer" @click="goToQCM">📝 S'entraîner avec un QCM</UButton>
      </div>
    </div>
  </div>
</template>
