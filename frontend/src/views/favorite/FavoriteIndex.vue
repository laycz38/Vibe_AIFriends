<script setup>
import { onMounted, ref } from 'vue'
import NoteCard from '../../components/NoteCard.vue'
import api from '@/js/http/api.js'

const notes = ref([])
const loading = ref(true)
const errorMessage = ref('')

async function loadFavorites() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await api.get('/api/notes/favorites/')
    notes.value = response.data.notes || []
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '加载收藏列表失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadFavorites()
})
</script>

<template>
  <div class="flex flex-col items-center mb-12 px-4">
    <h1 class="text-2xl font-bold mt-12 mb-2">我的收藏</h1>
    <p class="text-sm text-base-content/40 mb-6">你收藏的所有面经笔记</p>

    <div v-if="loading" class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 w-full px-9 justify-items-center">
      <div v-for="item in 4" :key="item" class="w-60 h-72 rounded-2xl bg-base-200 animate-pulse"></div>
    </div>

    <div v-else-if="errorMessage" class="alert alert-error max-w-180 mt-4">
      <span>{{ errorMessage }}</span>
    </div>

    <div v-else-if="notes.length === 0" class="card bg-base-200 shadow-sm max-w-180 mt-4">
      <div class="card-body text-center">
        <h2 class="text-xl font-bold">还没有收藏过面经</h2>
        <p class="text-base-content/60 mt-2">
          浏览首页看到有用的面经，点击卡片下方的 ☆ 标即可收藏。
        </p>
      </div>
    </div>

    <div v-else class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 w-full px-9 justify-items-center">
      <NoteCard v-for="note in notes" :key="note.id" :note="note" />
    </div>
  </div>
</template>
