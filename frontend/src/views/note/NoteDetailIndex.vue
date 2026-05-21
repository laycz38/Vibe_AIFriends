<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/js/http/api.js'
import { useUserStore } from '@/stores/user.js'

const props = defineProps({
  note_id: {
    type: String,
    required: true,
  },
})

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const likeLoading = ref(false)
const commentLoading = ref(false)
const errorMessage = ref('')
const note = ref(null)
const commentTextarea = ref(null)

const commentForm = reactive({
  content: '',
})

const timeLabel = computed(() => {
  if (!note.value?.created_at) return ''
  const d = new Date(note.value.created_at)
  const now = Date.now()
  const diff = now - d.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days} 天前`
  return d.toLocaleDateString('zh-CN')
})

function formatCommentTime(time) {
  const d = new Date(time)
  const now = Date.now()
  const diff = now - d.getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return '刚刚'
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days} 天前`
  return d.toLocaleDateString('zh-CN')
}

const DEFAULT_COVER = 'https://picsum.photos/seed/tech_office/1200/600'

function difficultyStyle(level) {
  const map = {
    '简单': 'badge badge-success',
    '中等': 'badge badge-warning',
    '困难': 'badge badge-error',
  }
  return map[level] || 'badge'
}

function requireLogin() {
  router.push({
    name: 'login',
    query: {
      redirect: route.fullPath,
    },
  })
}

function focusCommentBox() {
  commentTextarea.value?.focus()
}

async function loadNoteDetail() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await api.get(`/api/notes/${props.note_id}/`)
    note.value = response.data.note
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '加载面经详情失败'
  } finally {
    loading.value = false
  }
}

async function toggleLike() {
  if (!userStore.isLoggedIn) {
    requireLogin()
    return
  }

  likeLoading.value = true
  try {
    const response = await api.post(`/api/notes/${props.note_id}/toggle_like/`)
    if (note.value) {
      note.value.liked = response.data.liked
      note.value.likes = response.data.likes
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '点赞失败，请稍后重试'
  } finally {
    likeLoading.value = false
  }
}

async function submitComment() {
  if (!userStore.isLoggedIn) {
    requireLogin()
    return
  }

  commentLoading.value = true
  try {
    const response = await api.post(`/api/notes/${props.note_id}/comments/create/`, {
      content: commentForm.content,
    })
    if (note.value) {
      note.value.comments.unshift(response.data.comment)
      note.value.comment_count = response.data.comment_count
    }
    commentForm.content = ''
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '发表评论失败'
  } finally {
    commentLoading.value = false
  }
}

onMounted(() => {
  loadNoteDetail()
})

watch(() => props.note_id, () => {
  loadNoteDetail()
})
</script>

<template>
  <div class="flex flex-col items-center mb-12 px-4">
    <RouterLink :to="{ name: 'home' }" class="self-start mb-6 btn btn-ghost text-base">
      ← 返回首页
    </RouterLink>

    <div v-if="loading" class="card w-full max-w-180 bg-base-200 shadow-sm mt-4">
      <div class="card-body">
        <div class="h-8 w-3/4 bg-base-300 animate-pulse rounded mb-4"></div>
        <div class="h-4 w-full bg-base-300 animate-pulse rounded mb-2"></div>
        <div class="h-4 w-full bg-base-300 animate-pulse rounded mb-2"></div>
        <div class="h-4 w-2/3 bg-base-300 animate-pulse rounded"></div>
      </div>
    </div>

    <div v-else-if="errorMessage && !note" class="alert alert-error max-w-180">
      <span>{{ errorMessage }}</span>
    </div>

    <template v-else-if="note">
      <div class="card w-full max-w-180 bg-base-200 shadow-sm mt-4">
        <img :src="note.image || DEFAULT_COVER" :alt="note.title" class="w-full h-64 object-cover rounded-t-2xl" />
        <div class="card-body">
          <div class="flex items-center gap-2 mb-4">
            <span class="badge badge-neutral">{{ note.company }}</span>
            <span :class="difficultyStyle(note.difficulty)">{{ note.difficulty }}</span>
            <span class="badge badge-ghost">{{ note.position }}</span>
          </div>

          <h1 class="text-2xl font-bold">{{ note.title }}</h1>

          <RouterLink
            :to="`/user/${note.author_id}/`"
            class="flex items-center gap-2 mt-3"
          >
            <div class="avatar">
              <div class="w-8 rounded-full">
                <img v-if="note.avatar" :src="note.avatar" :alt="note.author" />
                <div
                  v-else
                  class="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-xs font-semibold text-indigo-700"
                >
                  {{ (note.author || 'U').slice(0, 1) }}
                </div>
              </div>
            </div>
            <span class="text-sm font-medium">{{ note.author }}</span>
            <span class="text-xs text-base-content/40">{{ timeLabel }}</span>
          </RouterLink>

          <div class="flex items-center gap-4 mt-4">
            <button
              class="btn btn-ghost gap-1"
              :class="{ 'text-error': note.liked }"
              :disabled="likeLoading"
              @click="toggleLike"
            >
              <svg class="size-5" viewBox="0 0 24 24" :fill="note.liked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2">
                <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
              </svg>
              <span>{{ note.likes }}</span>
            </button>
            <button class="btn btn-ghost gap-1" @click="focusCommentBox">
              <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <span>{{ note.comment_count }}</span>
            </button>
          </div>

          <div class="divider my-2"></div>

          <div class="whitespace-pre-line text-base leading-8 text-base-content/80">
            {{ note.content }}
          </div>
        </div>
      </div>

      <div class="card w-full max-w-180 bg-base-200 shadow-sm mt-8">
        <div class="card-body">
          <h2 class="text-lg font-bold">评论 ({{ note.comment_count }})</h2>

          <form class="mt-4" @submit.prevent="submitComment">
            <textarea
              ref="commentTextarea"
              v-model="commentForm.content"
              class="textarea textarea-bordered w-full h-24"
              placeholder="补充你的面试问题、准备建议或追问思路..."
            ></textarea>
            <button
              class="btn btn-neutral mt-3 w-full"
              :disabled="commentLoading"
            >
              {{ commentLoading ? '发布中...' : '发布评论' }}
            </button>
          </form>

          <p v-if="errorMessage" class="text-sm text-red-500 mt-3">{{ errorMessage }}</p>

          <div class="mt-6 space-y-4">
            <div
              v-for="comment in note.comments"
              :key="comment.id"
              class="chat chat-start"
            >
              <div class="chat-image avatar">
                <div class="w-10 rounded-full">
                  <img v-if="comment.avatar" :src="comment.avatar" :alt="comment.author" />
                  <div
                    v-else
                    class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-xs font-semibold text-indigo-700"
                  >
                    {{ (comment.author || 'U').slice(0, 1) }}
                  </div>
                </div>
              </div>
              <div class="chat-header text-sm font-medium">
                {{ comment.author }}
                <time class="text-xs text-base-content/40 ml-2">{{ formatCommentTime(comment.created_at) }}</time>
              </div>
              <div class="chat-bubble">{{ comment.content }}</div>
            </div>

            <div
              v-if="!note.comments?.length"
              class="text-center text-sm text-base-content/40 py-4"
            >
              还没有评论，来抢沙发吧。
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
