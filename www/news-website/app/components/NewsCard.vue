

<script setup>
defineProps({
  title: { type: String, required: true },
  image: { type: String, required: true },
  date: { type: String, default: '' },
  author: { type: String, default: '' },
  preview: { type: String, default: '' },
  link: { type: String, required: true }
})
</script>

<template>
	<NuxtLink :to="link" class="block">
  <UCard class="max-w-sm w-full hover:shadow-lg transition">
    <div class="overflow-hidden rounded-t-lg">
      <img
        :src="image"
        :alt="title"
        class="w-full h-48 object-cover"
      >
    </div>

    <div class="p-4 flex flex-col gap-2">
      <h3 class="text-lg font-bold text-gray-900">
        {{ title }}
      </h3>
      
      <div class="text-sm text-gray-500 flex justify-between">
        <span>{{ author }}</span>
        <span>{{ date }}</span>
      </div>

      <p class="text-gray-700 text-sm line-clamp-3">
        {{ preview }}
      </p>
    </div>
  </UCard>
  </NuxtLink>
</template>
