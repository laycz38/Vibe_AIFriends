<script setup>
import { onMounted, ref } from 'vue'
import NoteCard from './NoteCard.vue'
import api from '@/js/http/api.js'

const notes = ref([])
const loading = ref(true)
const errorMessage = ref('')

async function loadNotes() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await api.get('/api/notes/')
    notes.value = response.data.notes || []
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '加载首页面经失败'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadNotes()
})
</script>

<template>
  <div v-if="loading" class="p-4 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
    <div
      v-for="item in 8"
      :key="item"
      class="h-72 rounded-2xl bg-gray-100 animate-pulse"
    ></div>
  </div>

  <div v-else-if="errorMessage" class="p-6">
    <div class="mx-auto max-w-2xl rounded-3xl border border-red-100 bg-red-50 p-6 text-sm text-red-500">
      {{ errorMessage }}
    </div>
  </div>

  <div v-else-if="notes.length === 0" class="p-6">
    <div class="mx-auto max-w-2xl rounded-3xl border border-gray-200 bg-white p-10 text-center shadow-sm">
      <h2 class="text-xl font-semibold text-gray-900">还没有面经内容</h2>
      <p class="mt-3 text-sm leading-6 text-gray-500">
        当前首页只展示真实发布的面经。你可以先登录，然后去“发布面经”创建第一篇内容。
      </p>
    </div>
  </div>

  <div v-else class="columns-2 gap-4 p-4 md:columns-3 lg:columns-4 xl:columns-5">
    <div
      v-for="note in notes"
      :key="note.id"
      class="break-inside-avoid mb-4"
    >
      <NoteCard :note="note" />
    </div>
  </div>
</template>
