
<script setup lang="ts">
import { useRoute } from 'vue-router'
import { useFetch } from '#imports'

const route = useRoute()
const id = route.params.id

const { data: article, pending, error } = await useFetch('/api/articles', {
  query: { id }
})
</script>

<template>
  <main class="flex-grow p-8 max-w-3xl mx-auto">
    <div v-if="pending" class="text-center text-gray-500">
      Loading article...
    </div>

    <div v-else-if="error" class="text-center text-red-500">
      Failed to load article.
    </div>

    <div v-else-if="article && article[0]" class="space-y-6">
      <h1 class="text-4xl font-bold">{{ article[0].title }}</h1>

      <div class="text-sm text-gray-500 flex justify-between">
        <span>By {{ article[0].author }}</span>
        <span>{{ new Date(article[0].date).toLocaleDateString('en-US', {
          year: 'numeric', month: 'long', day: 'numeric'
        }) }}</span>
      </div>

      <img
        v-if="article[0].image_id"
        :src="`/${article[0].image_id}`"
        :alt="article[0].title"
        class="w-full rounded-lg shadow"
      >

      <p class="text-lg text-gray-800 whitespace-pre-line">
        {{ article[0].content }}
      </p>
    </div>
  </main>
</template>
