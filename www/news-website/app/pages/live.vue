<script setup>
const config = useRuntimeConfig()

</script>

<template>
  <div class="min-h-screen flex flex-col bg-gray-900 text-white">

    <main class="flex-grow flex flex-col items-center justify-center px-4 py-8">
      <h1 class="text-4xl font-bold mb-6 text-center">📡 Live Broadcast</h1>

      <div class="w-full max-w-5xl aspect-video rounded-2xl overflow-hidden shadow-2xl border border-gray-700 bg-black">
        <video
          class="w-full h-full"
          :src="config.public.livestreamAddress"
          autoplay
          controls
          playsinline
        />
      </div>

      <p class="mt-6 text-gray-400 text-lg">
        Streaming live coverage from our newsroom.
      </p>
    </main>

  </div>
</template>
