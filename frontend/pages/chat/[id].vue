<script setup>
import { ref, onMounted } from "vue";
import { useRoute } from "vue-router";
import ChatHistory from "@/components/ChatHistory.vue";
import ChatMessage from "@/components/ChatMessage.vue";
import ChatInput from "@/components/ChatInput.vue";

const route = useRoute();
const messages = ref([]);
const chatId = route.params.id; // Récupération de l'ID depuis l'URL
const isLoading = ref(false); // Indicateur de chargement

// Fonction pour récupérer les messages d'une discussion spécifique
const fetchMessages = async () => {
  try {
    const res = await fetch(`http://localhost:5000/chats/${chatId}`);
    const data = await res.json();
    messages.value = data.messages;
  } catch (error) {
    console.error("Erreur lors du chargement des messages :", error);
  }
};

// Ajouter un nouveau message à la discussion
const addMessage = async (text) => {
  const newMessage = { text, isUser: true };
  messages.value.push(newMessage); // Ajout du message localement

  // Affichage du spinner en attendant la réponse
  isLoading.value = true;
  messages.value.push({ text: "", isUser: false, isLoading: true });

  // Envoyer le message au serveur
  try {
    await fetch(`http://localhost:5000/chats/${chatId}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(newMessage),
    });
  } catch (error) {
    console.error("Erreur lors de l'envoi du message :", error);
  }

  // Envoyer la requête au chatbot
  try {
    const response = await fetch("http://localhost:8000/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: newMessage.text }),
    });
    const data = await response.json();

    // Retirer le spinner et ajouter la réponse
    messages.value.pop();
    messages.value.push({ text: data[0].response, isUser: false });
    
    await fetch(`http://localhost:5000/chats/${chatId}/message`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: data[0].response, isUser: false }),
    });

  } catch (error) {
    console.error("Erreur lors de l'envoi du message au chat:", error);
  } finally {
    isLoading.value = false;
  }
};

// Charger les messages au montage du composant
onMounted(fetchMessages);
</script>

<template>
  <div class="flex h-screen bg-gray-100 p-4">
    <!-- ChatHistory sur la gauche -->
    <div class="w-1/4 hidden md:block">
      <ChatHistory />
    </div>

    <!-- Chat principal centré -->
    <div class="flex-1 flex items-center justify-center">
      <div class="w-full max-w-5xl bg-white rounded-lg shadow-lg flex flex-col h-full mr-auto">
        <div class="p-4 font-bold text-lg  text-center bg-gray-50 text-gray-600">💬 OnizukAI</div>

        <!-- Zone des messages -->
        <div class="flex-1 overflow-y-auto p-6 space-y-4">
          <div 
            v-for="(msg, index) in messages" 
            :key="index"
            class="flex"
            :class="{'justify-end': msg.isUser, 'justify-start': !msg.isUser}"
          >
            <div
              class="p-3 rounded-2xl shadow-md max-w-3xl flex items-center"
              :class="{
                'bg-blue-500 text-white': msg.isUser,
                'bg-gray-200 text-gray-900': !msg.isUser
              }"
            >
              <template v-if="msg.isLoading">
                <img src="https://api.iconify.design/svg-spinners:12-dots-scale-rotate.svg" class="h-6 w-6" />
              </template>
              <template v-else>
                {{ msg.text }}
              </template>
            </div>
          </div>
        </div>

        <!-- Barre de saisie -->
        <ChatInput @send="addMessage" class="border-t p-4" />
      </div>
    </div>
  </div>
</template>

<style scoped>
.space-y-4 > * + * {
  margin-top: 1rem;
}
</style>
