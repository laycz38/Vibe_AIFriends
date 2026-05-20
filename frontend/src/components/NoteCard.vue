<script setup>
import { RouterLink } from 'vue-router'

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

function difficultyStyle(level) {
  const map = {
    '简单': 'bg-green-100 text-green-700',
    '中等': 'bg-amber-100 text-amber-700',
    '困难': 'bg-red-100 text-red-700',
  }
  return map[level] || 'bg-gray-100 text-gray-600'
}
</script>

<template>
  <div
    class="group cursor-pointer rounded-2xl bg-white overflow-hidden shadow-sm hover:shadow-lg transition-all duration-300 hover:-translate-y-1"
  >
    <div class="relative overflow-hidden">
      <RouterLink :to="`/notes/${note.id}/`">
        <img
          v-if="note.image"
          :src="note.image"
          :alt="note.title"
          class="w-full object-cover transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
        />
        <div
          v-else
          class="flex h-52 w-full items-center justify-center bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 text-center text-sm font-medium text-indigo-700"
        >
          面经封面待补充
        </div>
      </RouterLink>
      <div class="absolute top-2 left-2 flex gap-1.5">
        <span
          class="px-2 py-0.5 rounded-md text-[11px] font-medium bg-white/90 backdrop-blur-sm text-gray-800 shadow-sm"
        >
          {{ note.company }}
        </span>
        <span
          class="px-2 py-0.5 rounded-md text-[11px] font-medium shadow-sm"
          :class="difficultyStyle(note.difficulty)"
        >
          {{ note.difficulty }}
        </span>
      </div>
    </div>
    <div class="p-3">
      <RouterLink :to="`/notes/${note.id}/`" class="block">
        <h3 class="text-sm text-gray-800 leading-5 line-clamp-2 font-normal hover:text-indigo-600 transition-colors">
          {{ note.title }}
        </h3>
      </RouterLink>
      <div class="flex items-center gap-1.5 mt-2">
        <span class="px-1.5 py-0.5 rounded text-[10px] bg-indigo-50 text-indigo-600 font-medium">
          {{ note.position }}
        </span>
        <span class="px-1.5 py-0.5 rounded text-[10px] bg-gray-100 text-gray-500 font-medium">
          评论 {{ note.comment_count || 0 }}
        </span>
      </div>
      <div class="flex items-center justify-between mt-2">
        <div class="flex items-center gap-2">
          <img
            v-if="note.avatar"
            :src="note.avatar"
            :alt="note.author"
            class="w-5 h-5 rounded-full object-cover"
          />
          <div
            v-else
            class="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-100 text-[10px] font-semibold text-indigo-700"
          >
            {{ note.author?.slice(0, 1) || 'U' }}
          </div>
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
