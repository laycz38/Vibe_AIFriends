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

const formattedCreatedAt = computed(() => {
  if (!note.value?.created_at) return ''
  return new Date(note.value.created_at).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
})

function formatCommentTime(time) {
  return new Date(time).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
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
  <section class="p-6">
    <div v-if="loading" class="mx-auto max-w-7xl">
      <div class="grid gap-6 lg:grid-cols-[minmax(0,1.6fr)_380px]">
        <div class="h-[720px] rounded-[32px] bg-gray-100 animate-pulse"></div>
        <div class="h-[720px] rounded-[32px] bg-gray-100 animate-pulse"></div>
      </div>
    </div>

    <div v-else-if="errorMessage && !note" class="mx-auto max-w-3xl rounded-[32px] border border-red-100 bg-red-50 p-8 text-red-500">
      {{ errorMessage }}
    </div>

    <div v-else-if="note" class="mx-auto max-w-7xl">
      <div class="mb-6 flex items-center justify-between">
        <RouterLink
          to="/"
          class="inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-sm text-gray-500 shadow-sm hover:text-indigo-600"
        >
          <span>←</span>
          <span>返回首页</span>
        </RouterLink>
        <div class="rounded-full bg-white px-4 py-2 text-xs text-gray-400 shadow-sm">
          发布于 {{ formattedCreatedAt }}
        </div>
      </div>

      <div class="grid gap-6 lg:grid-cols-[minmax(0,1.6fr)_380px]">
        <article class="overflow-hidden rounded-[32px] bg-white shadow-sm">
          <div class="relative">
            <img
              v-if="note.image"
              :src="note.image"
              :alt="note.title"
              class="h-[420px] w-full object-cover"
            />
            <div
              v-else
              class="flex h-[420px] items-center justify-center bg-gradient-to-br from-indigo-100 via-purple-100 to-pink-100 text-lg font-semibold text-indigo-700"
            >
              这篇面经还没有上传封面
            </div>
            <div class="absolute inset-0 bg-gradient-to-t from-black/45 via-black/5 to-transparent"></div>
            <div class="absolute left-6 top-6 flex flex-wrap gap-2">
              <span class="rounded-full bg-white/90 px-3 py-1 text-xs font-medium text-gray-800 backdrop-blur">
                {{ note.company }}
              </span>
              <span class="rounded-full bg-white/90 px-3 py-1 text-xs font-medium text-indigo-700 backdrop-blur">
                {{ note.position }}
              </span>
              <span class="rounded-full bg-white/90 px-3 py-1 text-xs font-medium text-rose-500 backdrop-blur">
                {{ note.difficulty }}
              </span>
            </div>
            <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
              <h1 class="max-w-4xl text-3xl font-bold leading-tight md:text-4xl">
                {{ note.title }}
              </h1>
            </div>
          </div>

          <div class="p-8">
            <div class="flex flex-wrap items-center justify-between gap-4 border-b border-gray-100 pb-6">
              <div class="flex items-center gap-3">
                <img
                  v-if="note.avatar"
                  :src="note.avatar"
                  :alt="note.author"
                  class="h-11 w-11 rounded-full object-cover"
                />
                <div
                  v-else
                  class="flex h-11 w-11 items-center justify-center rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700"
                >
                  {{ note.author?.slice(0, 1) || 'U' }}
                </div>
                <div>
                  <p class="text-base font-semibold text-gray-900">{{ note.author }}</p>
                  <p class="text-sm text-gray-400">分享真实面试体验与复盘</p>
                </div>
              </div>

              <div class="flex flex-wrap gap-3 text-sm text-gray-500">
                <div class="rounded-2xl bg-gray-50 px-4 py-2">点赞 {{ note.likes }}</div>
                <div class="rounded-2xl bg-gray-50 px-4 py-2">评论 {{ note.comment_count }}</div>
              </div>
            </div>

            <div class="mt-8">
              <h2 class="mb-4 text-lg font-semibold text-gray-900">面经正文</h2>
              <div class="rounded-[28px] bg-[#fafafa] p-6 text-[15px] leading-8 text-gray-700 whitespace-pre-line">
                {{ note.content }}
              </div>
            </div>
          </div>
        </article>

        <aside class="space-y-6">
          <div class="sticky top-[108px] space-y-6">
            <div class="rounded-[32px] bg-white p-6 shadow-sm">
              <h2 class="text-lg font-semibold text-gray-900">互动操作</h2>
              <p class="mt-2 text-sm leading-6 text-gray-500">
                点赞代表这篇面经对你有帮助，评论可以补充问题、交流准备思路。
              </p>

              <div class="mt-6 grid gap-3">
                <button
                  class="flex items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-medium transition-colors"
                  :class="note.liked ? 'bg-rose-500 text-white hover:bg-rose-600' : 'bg-rose-50 text-rose-500 hover:bg-rose-100'"
                  :disabled="likeLoading"
                  @click="toggleLike"
                >
                  <span>{{ note.liked ? '已点赞' : '点赞这篇面经' }}</span>
                  <span>{{ note.likes }}</span>
                </button>
                <button
                  class="rounded-2xl bg-gray-100 px-4 py-3 text-sm font-medium text-gray-600 hover:bg-gray-200 transition-colors"
                  @click="focusCommentBox"
                >
                  写评论
                </button>
              </div>

              <div class="mt-6 rounded-[28px] border border-indigo-100 bg-indigo-50 p-4 text-sm text-indigo-700">
                <p class="font-medium">这篇面经适合谁看？</p>
                <p class="mt-2 leading-6">
                  准备 {{ note.company }} {{ note.position }} 方向的同学，可以先点赞收藏，再结合评论区补充问题做专项复习。
                </p>
              </div>
            </div>

            <div class="rounded-[32px] bg-white p-6 shadow-sm">
              <div class="flex items-center justify-between">
                <h2 class="text-lg font-semibold text-gray-900">评论区</h2>
                <span class="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-500">{{ note.comment_count }} 条</span>
              </div>

              <form class="mt-5 space-y-3" @submit.prevent="submitComment">
                <textarea
                  ref="commentTextarea"
                  v-model="commentForm.content"
                  class="min-h-[120px] w-full rounded-[24px] border border-gray-200 px-4 py-3 text-sm outline-none focus:border-indigo-500"
                  placeholder="补充你的面试问题、准备建议或追问思路..."
                ></textarea>
                <button
                  class="w-full rounded-2xl bg-indigo-600 px-4 py-3 text-sm font-medium text-white hover:bg-indigo-700 transition-colors disabled:cursor-not-allowed disabled:opacity-60"
                  :disabled="commentLoading"
                >
                  {{ commentLoading ? '发布中...' : '发布评论' }}
                </button>
              </form>

              <p v-if="errorMessage" class="mt-3 text-sm text-red-500">{{ errorMessage }}</p>

              <div class="mt-6 space-y-4">
                <div
                  v-for="comment in note.comments"
                  :key="comment.id"
                  class="rounded-[24px] bg-gray-50 p-4"
                >
                  <div class="flex items-center gap-3">
                    <img
                      v-if="comment.avatar"
                      :src="comment.avatar"
                      :alt="comment.author"
                      class="h-9 w-9 rounded-full object-cover"
                    />
                    <div
                      v-else
                      class="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-xs font-semibold text-indigo-700"
                    >
                      {{ comment.author?.slice(0, 1) || 'U' }}
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm font-medium text-gray-900">{{ comment.author }}</p>
                      <p class="text-xs text-gray-400">{{ formatCommentTime(comment.created_at) }}</p>
                    </div>
                  </div>
                  <p class="mt-3 whitespace-pre-line text-sm leading-7 text-gray-600">
                    {{ comment.content }}
                  </p>
                </div>

                <div
                  v-if="!note.comments?.length"
                  class="rounded-[24px] border border-dashed border-gray-200 px-4 py-8 text-center text-sm text-gray-400"
                >
                  还没有评论，来抢沙发吧。
                </div>
              </div>
            </div>
          </div>
        </aside>
      </div>
    </div>
  </section>
</template>
