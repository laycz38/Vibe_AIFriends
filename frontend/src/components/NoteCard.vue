<script setup>
defineProps({
  note: {
    type: Object,
    required: true,
  },
})

function formatLikes(num) {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  return num
}
</script>

<template>
  <div
    class="group cursor-pointer rounded-2xl bg-white overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
  >
    <div class="overflow-hidden">
      <img
        :src="note.image"
        :alt="note.title"
        class="w-full object-cover transition-transform duration-300 group-hover:scale-105"
        loading="lazy"
      />
    </div>
    <div class="p-3">
      <h3 class="text-sm text-gray-800 leading-5 line-clamp-2 font-normal">
        {{ note.title }}
      </h3>
      <div class="flex items-center justify-between mt-2">
        <div class="flex items-center gap-2">
          <img
            :src="note.avatar"
            :alt="note.author"
            class="w-5 h-5 rounded-full object-cover"
          />
          <span class="text-xs text-gray-400 truncate max-w-[80px]">
            {{ note.author }}
          </span>
        </div>
        <div class="flex items-center gap-1 text-gray-400">
          <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
          </svg>
          <span class="text-xs">{{ formatLikes(note.likes) }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
