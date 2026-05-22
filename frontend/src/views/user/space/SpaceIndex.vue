<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import api from '@/js/http/api.js'
import { useUserStore } from '@/stores/user.js'
import NoteCard from '@/components/NoteCard.vue'
import NoteEditModal from '@/components/NoteEditModal.vue'
import UserInfoField from './components/UserInfoField.vue'

const props = defineProps({
  user_id: {
    type: String,
    required: true,
  },
})

const userStore = useUserStore()
const userProfile = ref(null)
const notes = ref([])
const page = ref(1)
const hasMore = ref(true)
const isLoading = ref(false)
const sentinelRef = ref(null)
const pageSize = 12

const editingNote = ref(null)
const showEditModal = ref(false)

const isOwnSpace = computed(() =>
  userStore.user?.id === Number(props.user_id),
)

let observer = null

async function loadUserProfile() {
  try {
    const response = await api.get(`/api/user/${props.user_id}/profile/`)
    if (response.data?.result === 'success') {
      userProfile.value = response.data.user
    }
  } catch (_) {}
}

async function loadMore() {
  if (isLoading.value || !hasMore.value) return
  isLoading.value = true

  try {
    const response = await api.get('/api/notes/', {
      params: {
        user_id: props.user_id,
        page: page.value,
        page_size: pageSize,
      },
    })

    if (response.data?.result === 'success') {
      const newNotes = response.data.notes || []
      notes.value.push(...newNotes)
      page.value += 1
      if (newNotes.length < pageSize) {
        hasMore.value = false
      }
    }
  } catch (_) {
    hasMore.value = false
  } finally {
    isLoading.value = false
  }
}

function setupObserver() {
  if (observer) observer.disconnect()
  observer = new IntersectionObserver(
    (entries) => {
      if (entries[0]?.isIntersecting) {
        loadMore()
      }
    },
    { threshold: 0.1 },
  )
  if (sentinelRef.value) {
    observer.observe(sentinelRef.value)
  }
}

function resetAndLoad() {
  userProfile.value = null
  notes.value = []
  page.value = 1
  hasMore.value = true
  isLoading.value = false
  loadUserProfile()
  loadMore()
}

watch(() => props.user_id, () => {
  resetAndLoad()
})

onMounted(() => {
  resetAndLoad()
  setupObserver()
})

onBeforeUnmount(() => {
  if (observer) observer.disconnect()
})

function handleEdit(note) {
  editingNote.value = note
  showEditModal.value = true
}

function handleUpdated(updatedNote) {
  const idx = notes.value.findIndex((n) => n.id === updatedNote.id)
  if (idx !== -1) {
    notes.value[idx] = { ...notes.value[idx], ...updatedNote }
  }
  showEditModal.value = false
}

async function handleDelete(note) {
  if (!window.confirm('确定要删除这篇面经吗？此操作不可撤销。')) return

  try {
    const response = await api.delete(`/api/notes/${note.id}/delete/`)
    if (response.data?.result === 'success') {
      notes.value = notes.value.filter((n) => n.id !== note.id)
    }
  } catch (_) {}
}
</script>

<template>
  <section class="flex flex-col items-center p-6">
    <UserInfoField :user-profile="userProfile" />

    <div class="divider max-w-4xl mt-8"></div>

    <div class="w-full max-w-6xl mt-6">
      <div
        v-if="notes.length > 0"
        class="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-6 justify-items-center"
      >
        <NoteCard
          v-for="note in notes"
          :key="note.id"
          :note="note"
          :can-edit="isOwnSpace"
          @edit="handleEdit"
          @delete="handleDelete"
        />
      </div>

      <div
        v-if="notes.length === 0 && !isLoading"
        class="text-center py-16 text-base-content/50"
      >
        <p class="text-lg">暂无面经</p>
        <p class="text-sm mt-2">该用户还没有发布过面经笔记</p>
      </div>

      <div ref="sentinelRef" class="h-1"></div>

      <div v-if="isLoading" class="text-center py-8 text-base-content/50">
        <span class="loading loading-spinner loading-sm"></span>
        <span class="ml-2 text-sm">加载中...</span>
      </div>

      <div
        v-if="!hasMore && notes.length > 0 && !isLoading"
        class="text-center py-8 text-sm text-base-content/40"
      >
        没有更多了
      </div>
    </div>

    <NoteEditModal
      :note="editingNote"
      :visible="showEditModal"
      @close="showEditModal = false"
      @updated="handleUpdated"
    />
  </section>
</template>
