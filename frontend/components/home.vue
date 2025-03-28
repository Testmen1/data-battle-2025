<script setup>
import { useRouter } from "vue-router";
const router = useRouter();

</script>


<template>
    <div class="flex justify-between mb-4">
    <UButton icon="i-heroicons-home" color="secondary" variant="ghost" @click="router.push('/')"/>
  </div>
</template>