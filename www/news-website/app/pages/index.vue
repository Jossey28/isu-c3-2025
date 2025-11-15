<script setup lang="ts">
import 'vue3-carousel/dist/carousel.css'
import { Carousel, Slide, Navigation, Pagination } from 'vue3-carousel'
import { useFetch } from '#imports'

const { data: topStories, pending: topLoading, error: topError } = await useFetch('/api/articles', {
  query: { category: 'Breaking' }
})

const { data: latestArticles, pending: latestLoading, error: latestError } = await useFetch('/api/articles', {
  query: { category: 'Latest' }
})
</script>

<template>
  <div class="max-w-7xl mx-auto px-4 py-8">
		<p class="text-xs text-gray-500 italic mb-6">
      * All articles are parody and not intended to be taken as factual reporting.
    </p>
    <section class="mb-12">
      <h2 class="text-2xl font-bold mb-4">Top Stories</h2>
      <div v-if="topLoading" class="text-center text-gray-500">Loading top stories...</div>
      <div v-else-if="topError" class="text-center text-red-500">Failed to load top stories.</div>
      <Carousel v-else :items-to-show="1" :wrap-around="true" :autoplay="5000">
        <Slide v-for="story in topStories" :key="story.id">
          <NewsCard
            :title="story.title"
            :image="`/${story.image_id}`"
            :date="new Date(story.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })"
            :author="story.author"
            :preview="story.content.slice(0, 150) + '...'"
            :link="`/articles/${story.id}`"
            class="h-[400px]"
          />
        </Slide>
        <template #addons>
          <Navigation />
          <Pagination />
        </template>
      </Carousel>
    </section>

    <section>
      <h2 class="text-2xl font-bold mb-4">Latest News</h2>
      <div v-if="latestLoading" class="text-center text-gray-500">Loading latest articles...</div>
      <div v-else-if="latestError" class="text-center text-red-500">Failed to load latest articles.</div>
      <div v-else class="grid md:grid-cols-3 gap-6">
        <NewsCard
          v-for="article in latestArticles"
          :key="article.id"
          :title="article.title"
          :image="`/${article.image_id}`"
          :date="new Date(article.date).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })"
          :author="article.author"
          :preview="article.content.slice(0, 150) + '...'"
          :link="`/articles/${article.id}`"
        />
      </div>
    </section>
  </div>
</template>
