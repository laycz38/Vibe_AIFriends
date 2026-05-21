<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'

const DEFAULT_COVER = 'https://picsum.photos/seed/tech_office/800/600'

defineProps({
  note: {
    type: Object,
    required: true,
  },
})

const isHover = ref(false)

function formatLikes(num) {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  return num
}

function difficultyStyle(level) {
  const map = {
    '简单': 'bg-green-100 text-green-700',
    '中等': 'bg-yellow-100 text-yellow-700',
    '困难': 'bg-red-100 text-red-700',
  }
  return map[level] || 'bg-gray-100 text-gray-600'
}
</script>

<template>
  <div>
    <RouterLink :to="`/notes/${note.id}/`" class="cursor-pointer" @mouseover="isHover = true" @mouseout="isHover = false">
      <div class="w-60 h-72 rounded-2xl relative overflow-hidden">
        <img
          :src="note.image || DEFAULT_COVER"
          :alt="note.title"
          class="w-full h-full object-cover transition-transform duration-300"
          :class="{ 'scale-120': isHover }"
        />

        <div class="absolute left-0 bottom-0 w-full h-1/2 bg-gradient-to-t from-black/40 to-transparent"></div>

        <span class="absolute top-2 left-2 px-2 py-0.5 rounded-md text-[11px] font-medium bg-white/90 backdrop-blur-sm text-gray-800">
          {{ note.company }}
        </span>
        <span
          class="absolute top-2 right-2 px-2 py-0.5 rounded-md text-[11px] font-medium"
          :class="difficultyStyle(note.difficulty)"
        >
          {{ note.difficulty }}
        </span>

        <div class="absolute bottom-3 left-3 right-3">
          <div class="text-white font-bold text-sm line-clamp-2 leading-snug">
            {{ note.title }}
          </div>
          <div class="mt-1.5 flex items-center gap-2">
            <span class="px-1.5 py-0.5 rounded text-[10px] bg-white/20 text-white">{{ note.position }}</span>
            <span class="text-[10px] text-white/70">{{ note.comment_count || 0 }} 评论</span>
          </div>
        </div>
      </div>
    </RouterLink>

    <div class="flex items-center justify-between mt-3 w-60">
      <RouterLink :to="`/user/${note.author_id}/`" class="flex items-center gap-2">
        <img
          v-if="note.avatar"
          :src="note.avatar"
          :alt="note.author"
          class="w-6 h-6 rounded-full object-cover"
        />
        <div
          v-else
          class="w-6 h-6 rounded-full bg-indigo-100 flex items-center justify-center text-[10px] font-semibold text-indigo-700"
        >
          {{ (note.author || 'U').slice(0, 1) }}
        </div>
        <span class="text-sm text-base-content/70 line-clamp-1">{{ note.author }}</span>
      </RouterLink>
      <div class="flex items-center gap-1 text-base-content/40">
        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
        </svg>
        <span class="text-xs">{{ formatLikes(note.likes) }}</span>
      </div>
    </div>
  </div>
</template>
