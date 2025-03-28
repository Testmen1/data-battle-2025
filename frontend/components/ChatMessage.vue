<script setup>
defineProps({
  message: String,
  isUser: Boolean,
});
</script>

<template>
  <div
    class="flex my-2"
    :class="isUser ? 'justify-end' : 'justify-start'"
  >
    <span
      class="p-3 rounded-2xl shadow-md max-w-xs text-white transition-all duration-300 transform"
      :class="isUser ? 'bg-blue-500' : 'bg-gray-700'"
    >
      {{ message }}
    </span>
  </div>
</template>
