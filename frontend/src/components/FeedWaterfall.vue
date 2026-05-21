<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import NoteCard from './NoteCard.vue'
import api from '@/js/http/api.js'

const route = useRoute()
const notes = ref([])
const loading = ref(true)
const errorMessage = ref('')

async function loadNotes() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await api.get('/api/notes/', {
      params: {
        search_query: route.query.q || '',
      },
    })
    notes.value = response.data.notes || []
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '加载首页面经失败'
  } finally {
    loading.value = false
  }
}

function reset() {
  notes.value = []
  loading.value = false
  errorMessage.value = ''
  loadNotes()
}

watch(() => route.query.q, () => {
  reset()
})

onMounted(() => {
  loadNotes()
})
</script>

<template>
  <div v-if="loading" class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 px-9">
    <div
      v-for="item in 8"
      :key="item"
      class="w-60 h-72 rounded-2xl bg-base-200 animate-pulse"
    ></div>
  </div>

  <div v-else-if="errorMessage" class="mt-12 px-9">
    <div class="alert alert-error">
      <span>{{ errorMessage }}</span>
    </div>
  </div>

  <div v-else-if="notes.length === 0" class="mt-12 px-9">
    <div class="card bg-base-200 shadow-sm">
      <div class="card-body text-center">
        <h2 class="text-xl font-bold">
          {{ route.query.q ? '没有找到相关面经' : '还没有面经内容' }}
        </h2>
        <p class="text-base-content/60">
          {{ route.query.q ? '换个关键词试试吧' : '你可以先登录，然后去发布第一篇面经。' }}
        </p>
      </div>
    </div>
  </div>

  <div v-else class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-9 mt-12 px-9 justify-items-center w-full">
    <NoteCard v-for="note in notes" :key="note.id" :note="note" />
  </div>
</template>
