<script setup lang="ts">
import {  computed } from '#imports';

const config = useRuntimeConfig()

const weatherConditions = ['sunny', 'cloudy', 'rainy', 'thunderstorm']

const { data: weatherData, error, pending } = await useFetch('/api/weather', {
  headers: {
    'x-api-key-flag': config.public.apiKeyFlag
  }
})

const weather = computed(() => {
  if (!weatherData.value) return null
  return {
    ...weatherData.value,
    weather: weatherConditions[Math.floor(Math.random() * weatherConditions.length)]
  }
})
const weatherStyles = computed(() => {
  if (!weather.value?.weather) return {};
  
  const condition = weather.value.weather.toLowerCase();
  
  const styles = {
    sunny: {
      background: 'linear-gradient(135deg, #ffeb3b 0%, #ffc107 50%, #ff9800 100%)',
      cardBg: 'rgba(255, 255, 255, 0.9)',
      iconColor: '#ff9800',
      accentColor: '#76ff03'
    },
    cloudy: {
      background: 'linear-gradient(135deg, #9e9e9e 0%, #757575 50%, #616161 100%)',
      cardBg: 'rgba(255, 255, 255, 0.85)',
      iconColor: '#607d8b',
      accentColor: '#90a4ae'
    },
    rainy: {
      background: 'linear-gradient(135deg, #2196f3 0%, #1976d2 50%, #1565c0 100%)',
      cardBg: 'rgba(255, 255, 255, 0.9)',
      iconColor: '#0277bd',
      accentColor: '#03a9f4'
    },
thunderstorm: {
  background: 'linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%)',
  cardBg: 'rgba(255, 255, 255, 0.9)',
  iconColor: '#ffd600',
  accentColor: '#ffeb3b'
}
  };
  
  return styles[condition] || styles.sunny;
});

const weatherIcons = {
  sunny: '☀️',
  cloudy: '☁️',
  rainy: '🌧️',
  thunderstorm: '⛈️'
};

const getWeatherIcon = (condition: string) => {
  return weatherIcons[condition?.toLowerCase()] || '🌤️';
};


</script>





<template>
  <div 
    class="min-h-screen transition-all duration-1000 ease-in-out relative overflow-hidden"
    :style="{ background: weatherStyles.background }"
  >
    <!-- Animated background elements -->
    <div class="absolute inset-0 opacity-20">
      <div 
        v-if="weather?.weather === 'rainy'"
        class="absolute inset-0"
      >
        <div 
          v-for="i in 50" 
          :key="i"
          class="absolute w-0.5 h-8 bg-white opacity-60 animate-pulse rain-drop"
          :style="{
            left: Math.random() * 100 + '%',
            animationDelay: Math.random() * 2 + 's',
            animationDuration: (Math.random() * 1 + 0.5) + 's'
          }"
        />
      </div>
      <div v-if="weather?.weather === 'thunderstorm'" class="absolute inset-0">
  <div 
    v-for="i in 3" 
    :key="'lightning-' + i"
    class="absolute inset-0 bg-white opacity-0 lightning-flash"
    :style="{
      animationDelay: (Math.random() * 50) + 's',
      animationDuration: '0.2s'
    }"
  />
</div>
      <div 
        v-if="weather?.weather === 'sunny'"
        class="absolute top-10 right-10 w-32 h-32 rounded-full bg-yellow-300 opacity-30 animate-pulse"
      />
    </div>

    <div class="relative z-10 max-w-4xl mx-auto py-12 px-4">
      <!-- Header -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-white mb-2 drop-shadow-lg">
          Weather Report
        </h1>
        <p class="text-white/80 text-lg">
          Current conditions and forecast
        </p>
      </div>

      <div v-if="pending" class="text-center">
        <div 
          class="inline-block w-8 h-8 border-4 border-white/30 border-t-white rounded-full animate-spin"
        />
        <p class="text-white mt-4 text-lg">Loading weather data...</p>
      </div>

      <div v-else-if="error" class="text-center">
        <div class="bg-red-500/90 text-white p-6 rounded-xl backdrop-blur-sm">
          <h3 class="text-xl font-semibold mb-2">⚠️ Error Loading Weather</h3>
          <p>Unable to fetch weather information. Please try again later.</p>
        </div>
      </div>

      <div v-else class="space-y-6">
        <div 
          class="backdrop-blur-md rounded-2xl p-8 shadow-2xl border border-white/20 transition-all duration-500"
          :style="{ backgroundColor: weatherStyles.cardBg }"
        >
          <div class="flex items-center justify-between mb-6">
            <div class="flex items-center space-x-4">
              <div 
                class="text-6xl"
                :style="{ color: weatherStyles.iconColor }"
              >
                {{ getWeatherIcon(weather.weather) }}
              </div>
              <div>
                <h2 class="text-3xl font-bold text-gray-800 capitalize">
                  {{ weather.weather || 'Unknown' }}
                </h2>
                <p class="text-gray-600">Current conditions</p>
              </div>
            </div>
            <div class="text-right">
              <div class="text-5xl font-bold text-gray-800">
                {{ weather.temperature }}
              </div>
              <p class="text-gray-600">Temperature</p>
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="bg-white/50 rounded-xl p-4 backdrop-blur-sm">
              <div class="flex items-center space-x-3">
                <div 
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white text-lg"
                  :style="{ backgroundColor: weatherStyles.iconColor }"
                >
                  💧
                </div>
                <div>
                  <p class="text-sm text-gray-600 font-medium">Humidity</p>
                  <p class="text-xl font-bold text-gray-800">{{ weather.humidity }}</p>
                </div>
              </div>
            </div>

            <div class="bg-white/50 rounded-xl p-4 backdrop-blur-sm">
              <div class="flex items-center space-x-3">
                <div 
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white text-lg"
                  :style="{ backgroundColor: weatherStyles.iconColor }"
                >
                  💨
                </div>
                <div>
                  <p class="text-sm text-gray-600 font-medium">Wind Speed</p>
                  <p class="text-xl font-bold text-gray-800">{{ weather.wind_speed }}</p>
                </div>
              </div>
            </div>

            <div class="bg-white/50 rounded-xl p-4 backdrop-blur-sm">
              <div class="flex items-center space-x-3">
                <div 
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white text-lg"
                  :style="{ backgroundColor: weatherStyles.iconColor }"
                >
                  🌬️
                </div>
                <div>
                  <p class="text-sm text-gray-600 font-medium">Air Quality</p>
                  <p class="text-xl font-bold text-gray-800">{{ weather.air_quality }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div 
          class="backdrop-blur-md rounded-2xl p-6 shadow-xl border border-white/20"
          :style="{ backgroundColor: weatherStyles.cardBg }"
        >
          <h3 class="text-xl font-semibold text-gray-800 mb-4">Weather Details</h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div class="space-y-2">
              <div class="text-2xl">🌡️</div>
              <p class="text-sm text-gray-600">Feels Like</p>
              <p class="font-semibold text-gray-800">{{ weather.temperature }}</p>
            </div>
            <div class="space-y-2">
              <div class="text-2xl">👁️</div>
              <p class="text-sm text-gray-600">Visibility</p>
              <p class="font-semibold text-gray-800">Good</p>
            </div>
            <div class="space-y-2">
              <div class="text-2xl">📊</div>
              <p class="text-sm text-gray-600">Pressure</p>
              <p class="font-semibold text-gray-800">Normal</p>
            </div>
            <div class="space-y-2">
              <div class="text-2xl">☀️</div>
              <p class="text-sm text-gray-600">UV Index</p>
              <p class="font-semibold text-gray-800">Moderate</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
@keyframes rainDrop {
  0% {
    transform: translateY(-100vh);
    opacity: 1;
  }
  100% {
    transform: translateY(100vh);
    opacity: 0;
  }
}

.rain-drop {
  animation: rainDrop linear infinite;
}


@keyframes lightning {
  0% { opacity: 0; }
  10% { opacity: 1; }
  20% { opacity: 0; }
  30% { opacity: 1; }
  100% { opacity: 0; }
}

.lightning-flash {
  animation-name: lightning;
  animation-iteration-count: 1;
}
</style>
