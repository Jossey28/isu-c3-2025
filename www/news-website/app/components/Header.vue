
<script setup>

</script>

<template>
  <header class="sticky top-0 z-50 w-full border-b border-gray-200 bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
    <nav class="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
      <div class="flex items-center">
<NuxtLink to="/" class="flex items-center space-x-3">
  <!-- Logo Container -->
  <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-cyan-400 shadow-lg">
    <span class="text-white font-bold text-sm">CDC</span>
  </div>

  <!-- Logo Text -->
  <span class="text-2xl font-extrabold tracking-tight text-gray-900">
    News
  </span>
</NuxtLink>
      </div>

      <div class="hidden md:flex md:items-center md:space-x-8">
        <NuxtLink to="/live">
          <UButton
            color="neutral"
            variant="outline"
            size="xl"
          >
            <div class="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
            Live
          </UButton>  
        </NuxtLink>
        <NuxtLink to="/weather">
          <UButton
            color="neutral"
            variant="outline"
            icon="wi:day-hail"
            size="xl"
          >
            Weather
          </UButton>  
        </NuxtLink>
        <NuxtLink to="/technology">
          <UButton
            color="neutral"
            variant="outline"
            icon="icomoon-free:rss"
            size="xl"
          >
            Technology
          </UButton>  
        </NuxtLink>
      </div>
    </nav>
  </header>
</template>

