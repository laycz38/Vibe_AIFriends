<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import api from '@/js/http/api.js'
import { useUserStore } from '@/stores/user.js'
import { renderMarkdown, extractOutline } from '@/js/markdown.js'

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
const favLoading = ref(false)
const commentLoading = ref(false)
const errorMessage = ref('')
const note = ref(null)
const commentTextarea = ref(null)
const contentAreaRef = ref(null)
const activeHeadingId = ref('')
const showCoverModal = ref(false)
const coverScale = ref(1)
const coverPosition = ref({ x: 0, y: 0 })

function openCoverModal() {
  coverScale.value = 1
  coverPosition.value = { x: 0, y: 0 }
  showCoverModal.value = true
}

function closeCoverModal() {
  showCoverModal.value = false
  coverScale.value = 1
  coverPosition.value = { x: 0, y: 0 }
}

function zoomCover(delta) {
  coverScale.value = Math.max(0.5, Math.min(5, coverScale.value + delta * 0.002))
  if (coverScale.value <= 1) {
    coverPosition.value = { x: 0, y: 0 }
  }
}

function toggleCoverZoom() {
  if (coverScale.value > 1.1) {
    coverScale.value = 1
    coverPosition.value = { x: 0, y: 0 }
  } else {
    coverScale.value = 2
  }
}

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

const renderedContent = computed(() => {
  return renderMarkdown(note.value?.content || '')
})

const outline = computed(() => {
  return extractOutline(note.value?.content || '')
})

function scrollToHeading(id) {
  const el = document.getElementById(id)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'start' })
    activeHeadingId.value = id
  }
}

function setupScrollSpy() {
  if (!contentAreaRef.value) return
  const headings = contentAreaRef.value.querySelectorAll('h1[id], h2[id], h3[id], h4[id]')
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          activeHeadingId.value = entry.target.id
          break // use the first visible heading
        }
      }
    },
    { rootMargin: '-80px 0px -70% 0px' }
  )
  headings.forEach((h) => observer.observe(h))
}

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

import defaultCover from '@/assets/AI_interview_default.png'

const DEFAULT_COVER = defaultCover

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

async function toggleFavorite() {
  if (!userStore.isLoggedIn) {
    requireLogin()
    return
  }

  favLoading.value = true
  try {
    const response = await api.post(`/api/notes/${props.note_id}/toggle_favorite/`)
    if (note.value) {
      note.value.favorited = response.data.favorited
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '收藏失败，请稍后重试'
  } finally {
    favLoading.value = false
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

watch(renderedContent, async () => {
  await nextTick()
  setupScrollSpy()
})
</script>

<template>
  <div class="flex justify-center gap-10 mb-16 px-4 pt-6">
    <!-- ===== 左侧目录 ===== -->
    <aside
      v-if="outline.length"
      class="hidden xl:block w-52 shrink-0"
    >
      <nav class="sticky top-24 max-h-[calc(100vh-7rem)] overflow-y-auto">
        <h4 class="text-xs font-semibold mb-4 text-base-content/40 tracking-widest">目录</h4>
        <ul class="space-y-0">
          <li v-for="item in outline" :key="item.id">
            <a
              href="#"
              @click.prevent="scrollToHeading(item.id)"
              :style="{ paddingLeft: 0.5 + (item.level - 1) * 0.75 + 'rem' }"
              class="block py-1.5 pr-3 text-sm rounded-md transition-all duration-150 border-l-[3px]"
              :class="activeHeadingId === item.id
                ? 'text-primary border-primary bg-primary/5 font-semibold'
                : 'text-base-content/55 border-transparent hover:text-base-content/80 hover:bg-base-200/60'"
            >
              {{ item.text }}
            </a>
          </li>
        </ul>
      </nav>
    </aside>

    <!-- ===== 中间正文 ===== -->
    <div class="w-full max-w-[720px] min-w-0">
      <RouterLink
        :to="{ name: 'home' }"
        class="inline-flex items-center gap-1 text-sm text-base-content/40 hover:text-base-content mb-8 transition-colors"
      >
        <svg class="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
        返回首页
      </RouterLink>

      <!-- Loading -->
      <div v-if="loading" class="space-y-4 animate-pulse">
        <div class="flex gap-2"><div class="h-5 w-16 bg-base-300 rounded-full"></div><div class="h-5 w-12 bg-base-300 rounded-full"></div></div>
        <div class="h-9 w-3/4 bg-base-300 rounded-lg"></div>
        <div class="h-5 w-48 bg-base-300 rounded"></div>
        <div class="h-4 w-full bg-base-300 rounded mt-8"></div>
        <div class="h-4 w-full bg-base-300 rounded"></div>
        <div class="h-4 w-2/3 bg-base-300 rounded"></div>
      </div>

      <!-- Error -->
      <div v-else-if="errorMessage && !note" class="alert alert-error">
        <span>{{ errorMessage }}</span>
      </div>

      <!-- Article -->
      <template v-else-if="note">
      <article ref="contentAreaRef">
        <!-- Meta row -->
        <div class="flex flex-wrap items-center gap-2 mb-5">
          <span class="badge badge-neutral badge-sm font-normal">{{ note.company }}</span>
          <span :class="difficultyStyle(note.difficulty)" class="badge badge-sm font-normal">{{ note.difficulty }}</span>
          <span v-if="note.position" class="badge badge-ghost badge-sm font-normal">{{ note.position }}</span>
        </div>

        <!-- Title -->
        <h1 class="text-[1.75rem] leading-tight font-bold tracking-tight mb-6">{{ note.title }}</h1>

        <!-- Author + actions row -->
        <div class="flex items-center justify-between mb-5 pb-5 border-b border-base-300">
          <!-- Author -->
          <RouterLink :to="`/user/${note.author_id}/`" class="flex items-center gap-2.5 group">
            <div class="avatar">
              <div class="w-9 rounded-full">
                <img v-if="note.avatar" :src="note.avatar" :alt="note.author" />
                <div v-else class="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-xs font-semibold text-primary">
                  {{ (note.author || 'U').slice(0, 1) }}
                </div>
              </div>
            </div>
            <div class="leading-tight">
              <div class="text-sm font-semibold group-hover:text-primary transition-colors">{{ note.author }}</div>
              <div class="text-xs text-base-content/40">{{ timeLabel }}</div>
            </div>
          </RouterLink>

          <!-- Action icons -->
          <div class="flex items-center gap-1.5">
            <button class="btn btn-ghost btn-sm btn-square" :class="{ 'text-error': note.liked }" :disabled="likeLoading" @click="toggleLike" title="点赞">
              <svg class="size-4" viewBox="0 0 24 24" :fill="note.liked ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/></svg>
            </button>
            <span class="text-xs text-base-content/60 min-w-[1.25rem]">{{ note.likes }}</span>

            <button class="btn btn-ghost btn-sm btn-square" :class="{ 'text-amber-400': note.favorited }" :disabled="favLoading" @click="toggleFavorite" title="收藏">
              <svg class="size-4" viewBox="0 0 24 24" :fill="note.favorited ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
            </button>

            <button class="btn btn-ghost btn-sm btn-square" @click="focusCommentBox" title="评论">
              <svg class="size-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            </button>
            <span class="text-xs text-base-content/60">{{ note.comment_count }}</span>
          </div>
        </div>

        <!-- === CTA: 模拟面试（核心操作） === -->
        <RouterLink
          :to="{ name: 'friend', query: { interview: note.id } }"
          class="flex items-center justify-center gap-2.5 w-full py-3 mb-8 bg-primary hover:bg-primary/90 text-primary-content rounded-xl font-semibold text-[0.95rem] shadow-md shadow-primary/15 hover:shadow-lg hover:shadow-primary/25 transition-all duration-200 active:scale-[0.985]"
        >
          <svg class="size-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
          模拟面试：AI 实时追问练习
        </RouterLink>

        <!-- === 正文 === -->
        <div
          class="markdown-body text-[15px] leading-[1.8] text-base-content/85"
          v-html="renderedContent"
        ></div>
      </article>

      <!-- ===== 评论区 ===== -->
      <section class="mt-14 pt-10 border-t border-base-300">
        <h2 class="text-lg font-bold mb-6">评论 ({{ note.comment_count }})</h2>

        <form class="mb-8" @submit.prevent="submitComment">
          <textarea
            ref="commentTextarea"
            v-model="commentForm.content"
            class="textarea textarea-bordered w-full h-24 text-sm"
            placeholder="写下你的想法..."
          ></textarea>
          <div class="flex justify-end mt-3">
            <button class="btn btn-neutral btn-sm" :disabled="commentLoading">
              {{ commentLoading ? '发布中...' : '发布评论' }}
            </button>
          </div>
        </form>

        <p v-if="errorMessage" class="text-sm text-error mb-4">{{ errorMessage }}</p>

        <div class="space-y-5">
          <div v-for="comment in note.comments" :key="comment.id" class="chat chat-start">
            <div class="chat-image avatar">
              <div class="w-9 rounded-full">
                <img v-if="comment.avatar" :src="comment.avatar" :alt="comment.author" />
                <div v-else class="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center text-xs font-semibold text-primary">
                  {{ (comment.author || 'U').slice(0, 1) }}
                </div>
              </div>
            </div>
            <div class="chat-header text-sm font-semibold mb-0.5">
              {{ comment.author }}
              <time class="text-xs text-base-content/40 ml-2 font-normal">{{ formatCommentTime(comment.created_at) }}</time>
            </div>
            <div class="chat-bubble text-sm">{{ comment.content }}</div>
          </div>

          <div v-if="!note.comments?.length" class="text-center text-sm text-base-content/30 py-10">
            暂无评论
          </div>
        </div>
      </section>
    </template>

    <!-- Cover lightbox (unchanged) -->
    <div
      v-if="showCoverModal && note?.image"
      class="fixed inset-0 z-[100] flex items-center justify-center bg-black/85 p-4 overflow-hidden"
      @click.self="closeCoverModal"
      @wheel.prevent="zoomCover($event.deltaY)"
    >
      <div class="absolute top-4 left-4 right-4 flex items-center justify-between gap-2 z-10">
        <div class="flex items-center gap-2">
          <button class="btn btn-circle btn-ghost btn-sm text-white text-lg" @click="zoomCover(-100)">+</button>
          <span class="text-white text-sm font-mono w-12 text-center">{{ Math.round(coverScale * 100) }}%</span>
          <button class="btn btn-circle btn-ghost btn-sm text-white text-lg" @click="zoomCover(100)">−</button>
          <button class="btn btn-ghost btn-sm text-white text-xs" @click="coverScale = 1; coverPosition = { x: 0, y: 0 }">重置</button>
        </div>
        <button class="btn btn-circle btn-ghost text-white text-2xl" @click="closeCoverModal">✕</button>
      </div>
      <img
        :src="note.image"
        :alt="note.title"
        class="rounded-xl select-none"
        :class="coverScale > 1 ? 'cursor-grab' : 'cursor-pointer'"
        :style="{
          transform: `scale(${coverScale}) translate(${coverPosition.x / coverScale}px, ${coverPosition.y / coverScale}px)`,
          maxWidth: coverScale <= 1 ? '100%' : 'none',
          maxHeight: coverScale <= 1 ? '90vh' : 'none',
          objectFit: 'contain',
          transition: coverScale <= 1 ? 'transform 0.2s ease-out' : 'none',
        }"
        @click="toggleCoverZoom"
      />
    </div>
  </div><!-- end content column -->
  </div><!-- end outer flex -->
</template>

<style>
.markdown-body h1 { font-size: 1.6rem; font-weight: 700; margin: 2em 0 0.6em; padding-bottom: 0.3em; border-bottom: 1px solid var(--color-base-300); letter-spacing: -0.01em; }
.markdown-body h2 { font-size: 1.35rem; font-weight: 700; margin: 1.8em 0 0.5em; padding-bottom: 0.25em; border-bottom: 1px solid var(--color-base-300); letter-spacing: -0.01em; }
.markdown-body h3 { font-size: 1.15rem; font-weight: 600; margin: 1.5em 0 0.4em; }
.markdown-body h4 { font-size: 1.05rem; font-weight: 600; margin: 1.2em 0 0.3em; }
.markdown-body h1:first-child { margin-top: 0; }
.markdown-body p { margin: 1em 0; }
.markdown-body ul, .markdown-body ol { padding-left: 1.5em; margin: 0.8em 0; }
.markdown-body li { margin: 0.35em 0; }
.markdown-body li::marker { color: var(--color-base-content); opacity: 0.35; }
.markdown-body blockquote {
  border-left: 3px solid var(--color-primary);
  padding: 0.6em 1em;
  margin: 1.2em 0;
  background: color-mix(in srgb, var(--color-primary) 4%, transparent);
  border-radius: 0 8px 8px 0;
  opacity: 0.9;
}
.markdown-body blockquote p { margin: 0.3em 0; }
.markdown-body code {
  background: color-mix(in srgb, var(--color-base-content) 8%, transparent);
  padding: 0.15em 0.45em;
  border-radius: 5px;
  font-size: 0.88em;
  font-family: ui-monospace, 'Cascadia Code', 'Source Code Pro', Menlo, Consolas, monospace;
  font-weight: 450;
}
.markdown-body pre {
  background: #1b1b2c;
  color: #cdd6f4;
  padding: 1.1em 1.3em;
  border-radius: 10px;
  overflow-x: auto;
  margin: 1.2em 0;
  line-height: 1.55;
  font-size: 0.88em;
}
.markdown-body pre code {
  background: none;
  padding: 0;
  font-size: inherit;
  color: inherit;
}
.markdown-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.2em 0;
  font-size: 0.92em;
}
.markdown-body th {
  background: var(--color-base-200);
  font-weight: 600;
  padding: 0.65em 0.9em;
  border: 1px solid var(--color-base-300);
  text-align: left;
}
.markdown-body td {
  padding: 0.55em 0.9em;
  border: 1px solid var(--color-base-300);
}
.markdown-body tr:nth-child(even) td {
  background: color-mix(in srgb, var(--color-base-200) 50%, transparent);
}
.markdown-body hr {
  border: none;
  border-top: 1.5px solid var(--color-base-300);
  margin: 2em 0;
}
.markdown-body a {
  color: var(--color-primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.markdown-body strong { font-weight: 700; color: var(--color-base-content); }
.markdown-body img { max-width: 100%; border-radius: 10px; margin: 1em 0; }
.markdown-body > *:first-child { margin-top: 0 !important; }
.markdown-body > *:last-child { margin-bottom: 0 !important; }
</style>
