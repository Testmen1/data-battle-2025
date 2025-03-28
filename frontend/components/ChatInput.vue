<script setup>
import { ref } from "vue";

const emit = defineEmits(["send"]);
const message = ref("");

// Fonction pour envoyer le message
const sendMessage = () => {
  if (message.value.trim() === "") return; // Empêche d'envoyer un message vide
  emit("send", message.value);
  message.value = ""; // Réinitialise l'input après l'envoi
};

// Gérer l'appui sur "Entrée"
const handleKeyDown = (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault(); // Empêche le retour à la ligne dans l'input
    sendMessage();
  }
};
</script>

<template>
  <div class="flex gap-2 p-3 border-t bg-gray-100 rounded-b-lg">
    <UTextarea
    :rows="1" 
    v-model="message" 
    @keydown="handleKeyDown" 
    placeholder="Écris un message..." 
    class="flex-1"
    color="neutral"
    autoresize
  />

    <UButton icon="i-heroicons-paper-airplane" color="secondary" @click="sendMessage" />
  </div>
</template>
