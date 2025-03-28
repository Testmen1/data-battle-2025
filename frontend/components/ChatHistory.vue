<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import home from "@/components/home.vue";

const router = useRouter();
const chatHistory = ref([]);
const searchQuery = ref("");

const fetchChats = async () => {
  try {
    const res = await fetch("http://localhost:5000/chats");
    chatHistory.value = await res.json();
  } catch (error) {
    console.error("Erreur lors du chargement des chats :", error);
  }
};

const createNewChat = async () => {
  try {
    const title = `Discussion ${chatHistory.value.length + 1}`;
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
  } 
};

const deleteChat = async (id) => {
  try {
    const res = await fetch(`http://localhost:5000/chats/${id}`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
    });
    goToLatestChat();
  } catch (error) {
    console.error("Erreur lors de la supression du chat :", error);
  }
};
const openChat = (id) => {
  router.push(`/chat/${id}`);
};

onMounted(fetchChats);
</script>


<template>
  <div class="p-4 bg-gray-100 rounded-lg shadow-md h-full w-xs flex flex-col">
    <home />
    <div class="mb-2 flex">
      <UButton color="secondary" class="text-sm" @click="createNewChat">
        + Nouveau Chat
      </UButton>
    </div>
    <UInput v-model="searchQuery" placeholder="Rechercher une discussion..." icon="i-heroicons-magnifying-glass" class="mb-4 w-full" />
    <div class="flex-1 overflow-y-auto">
      <div>
        <div v-for="chat in chatHistory.filter(chat => chat.title.toLowerCase().includes(searchQuery.toLowerCase()))" :key="chat._id">
          <div class="p-2 hover:bg-gray-200 text-gray-600 rounded-lg cursor-pointer flex justify-between items-center" @click="openChat(chat._id)">
            <div>
              <p class="font-medium">{{ chat.title }}</p>
              <p class="text-sm text-gray-500" v-if="chat.messages.length > 0">{{ (chat.messages[chat.messages.length - 1].text || "Message non disponible").slice(0,60) }}</p>
            </div>
            <UButton icon="i-heroicons-trash" class="text-red-500" size="sm" color="error" variant="ghost" @click="deleteChat(chat._id)"/>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>