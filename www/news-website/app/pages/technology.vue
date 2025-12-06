
<script setup lang="ts">
import { useFetch } from '#imports'

const { data: articles, pending, error } = await useFetch('/api/articles', {
  query: { category: 'Technology' }
})
</script>

<template>
  <main class="flex-grow p-8">
    <h1 class="text-3xl font-bold mb-6">Technology News</h1>
		<p class="text-xs text-gray-500 italic mb-6">
      * All articles are parody and not intended to be taken as factual reporting.
    </p>

    <div v-if="pending" class="text-center text-gray-500">
      Loading articles...
    </div>

    <div v-else-if="error" class="text-center text-red-500">
      Failed to load articles.
    </div>

    <div v-else class="grid gap-6 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
      <NewsCard
        v-for="article in articles"
        :key="article.id"
        :title="article.title"
	:date="new Date(article.date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })"
	:author="article.author"
        :preview="article.content.slice(0, 100) + '...'"
        :image="`/${article.image_id}`"
        :link="`/articles/${article.id}`"
      />
    </div>
  </main>
</template>

