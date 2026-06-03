<script setup>
import { ref, watch, onMounted, onUnmounted, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user.js'
import api from '@/js/http/api.js'
import { CONTENT_SCRIPT } from './contentScript.js'

const userStore = useUserStore()
const router = useRouter()

const iframeRef = ref(null)
const panelOpen = ref(false)
const mobilePanelOpen = ref(false)
const activeTab = ref('page') // 'page' | 'annotations'

// Page-level note
const noteContent = ref('')
const noteSaveStatus = ref('')

// Inline annotations
const annotations = ref([])
const selectedText = ref(null) // { text, contextBefore, contextAfter }
const editingAnno = ref(null)  // { id?, content, selected_text } — null = not editing, no id = creating new
const annoSaveStatus = ref('')

let pollTimer = null
let pageSaveTimer = null
let annoSaveTimer = null
let lastSavedNote = ''
let lastSavedAnnoContent = ''

const currentPageUrl = ref('')
const isLoggedIn = computed(() => userStore.isLoggedIn)

const panelTitle = computed(() => {
  const path = currentPageUrl.value
  if (!path) return '学习笔记'
  const parts = path.split('/').filter(Boolean)
  const last = parts[parts.length - 1]
  if (last.endsWith('.html')) return last.replace('.html', '').replace(/_/g, ' ')
  const idx = parts.findIndex(p => p === 'nlp_notes')
  if (idx >= 0 && idx + 1 < parts.length) return parts[idx + 1].replace(/_/g, ' ')
  return '学习笔记'
})

// --- Iframe path tracking ---

function getIframePath() {
  try {
    if (iframeRef.value?.contentWindow) {
      return iframeRef.value.contentWindow.location.pathname
    }
  } catch (_) { /* not loaded yet */ }
  return ''
}

function detectPageChange() {
  const path = getIframePath()
  if (path && path !== currentPageUrl.value) {
    currentPageUrl.value = path
    loadPageData()
    injectContentScript()
  }
}

// --- Content script injection ---

function injectContentScript() {
  const iframe = iframeRef.value
  if (!iframe?.contentDocument) return
  const doc = iframe.contentDocument
  if (doc.getElementById('aifriends-cs')) return // already injected
  const script = doc.createElement('script')
  script.id = 'aifriends-cs'
  script.textContent = CONTENT_SCRIPT
  doc.head.appendChild(script)
}

// --- Load data for current page ---

async function loadPageData() {
  loadPageNote()
  await loadAnnotations()
  sendAnnotationsToIframe()
}

async function loadPageNote() {
  if (!isLoggedIn.value || !currentPageUrl.value) {
    noteContent.value = ''
    lastSavedNote = ''
    noteSaveStatus.value = ''
    return
  }
  try {
    const res = await api.get('/api/study-notes/', { params: { page_url: currentPageUrl.value } })
    if (res.data?.result === 'success') {
      noteContent.value = res.data.note?.content || ''
      lastSavedNote = noteContent.value
      noteSaveStatus.value = ''
    }
  } catch (_) { /* ignore */ }
}

async function loadAnnotations() {
  if (!isLoggedIn.value || !currentPageUrl.value) {
    annotations.value = []
    return
  }
  try {
    const res = await api.get('/api/inline-annotations/', { params: { page_url: currentPageUrl.value } })
    if (res.data?.result === 'success') {
      annotations.value = res.data.annotations || []
    }
  } catch (_) { /* ignore */ }
}

function sendAnnotationsToIframe() {
  const iframe = iframeRef.value
  if (!iframe?.contentWindow) return
  iframe.contentWindow.postMessage({
    type: 'render-annotations',
    annotations: annotations.value,
  }, '*')
}

// --- Page note save ---

async function savePageNote() {
  if (!isLoggedIn.value || !currentPageUrl.value) return
  if (noteContent.value === lastSavedNote) { noteSaveStatus.value = 'saved'; return }
  noteSaveStatus.value = 'saving'
  try {
    await api.post('/api/study-notes/save/', { page_url: currentPageUrl.value, content: noteContent.value })
    lastSavedNote = noteContent.value
    noteSaveStatus.value = 'saved'
  } catch (_) { noteSaveStatus.value = 'unsaved' }
}

watch(noteContent, () => {
  if (noteContent.value !== lastSavedNote) {
    clearTimeout(pageSaveTimer)
    noteSaveStatus.value = ''
    pageSaveTimer = setTimeout(savePageNote, 1500)
  }
})

// --- Annotation CRUD ---

function startNewAnnotation() {
  if (!selectedText.value) return
  editingAnno.value = {
    id: null,
    content: '',
    selected_text: selectedText.value.text,
  }
  annoSaveStatus.value = ''
  panelOpen.value = true
  activeTab.value = 'annotations'
}

function startEditAnnotation(ann) {
  editingAnno.value = {
    id: ann.id,
    content: ann.content,
    selected_text: ann.selected_text,
  }
  lastSavedAnnoContent = ann.content
  annoSaveStatus.value = ''
  panelOpen.value = true
  activeTab.value = 'annotations'
}

function cancelEditAnnotation() {
  editingAnno.value = null
  annoSaveStatus.value = ''
}

async function saveAnnotation() {
  if (!editingAnno.value || !isLoggedIn.value) return
  const anno = editingAnno.value
  annoSaveStatus.value = 'saving'
  try {
    if (anno.id) {
      // Update existing
      await api.put(`/api/inline-annotations/${anno.id}/`, { content: anno.content })
    } else {
      // Create new
      await api.post('/api/inline-annotations/create/', {
        page_url: currentPageUrl.value,
        selected_text: selectedText.value.text,
        context_before: selectedText.value.contextBefore,
        context_after: selectedText.value.contextAfter,
        content: anno.content,
      })
    }
    await loadAnnotations()
    sendAnnotationsToIframe()
    editingAnno.value = null
    selectedText.value = null
    annoSaveStatus.value = ''
  } catch (_) { annoSaveStatus.value = 'unsaved' }
}

async function deleteAnnotation(id) {
  if (!confirm('确定删除这条批注吗？')) return
  try {
    await api.delete(`/api/inline-annotations/${id}/delete/`)
    await loadAnnotations()
    sendAnnotationsToIframe()
    if (editingAnno.value?.id === id) cancelEditAnnotation()
  } catch (_) { /* ignore */ }
}

function requireLogin() {
  router.push({ name: 'login', query: { redirect: '/nlp-notes/' } })
}

// --- Handle messages from iframe ---

function onIframeMessage(e) {
  if (!e.data?.type) return
  switch (e.data.type) {
    case 'text-selected':
      if (!isLoggedIn.value) break
      selectedText.value = {
        text: e.data.text,
        contextBefore: e.data.contextBefore,
        contextAfter: e.data.contextAfter,
      }
      break
    case 'selection-cleared':
      // Don't clear if we're currently editing
      if (!editingAnno.value) selectedText.value = null
      break
    case 'annotation-click':
      const ann = annotations.value.find(a => a.id === e.data.id)
      if (ann) startEditAnnotation(ann)
      break
  }
}

// --- Lifecycle ---

function onIframeLoad() {
  injectContentScript()
  detectPageChange()
}

onMounted(() => {
  window.addEventListener('message', onIframeMessage)
  if (iframeRef.value) {
    iframeRef.value.addEventListener('load', onIframeLoad)
  }
  pollTimer = setInterval(detectPageChange, 2000)
})

onUnmounted(() => {
  window.removeEventListener('message', onIframeMessage)
  clearInterval(pollTimer)
  clearTimeout(pageSaveTimer)
  clearTimeout(annoSaveTimer)
  if (iframeRef.value) {
    iframeRef.value.removeEventListener('load', onIframeLoad)
  }
})
</script>

<template>
  <div class="flex w-full" style="height: calc(100vh - 4rem);">
    <!-- Left: NLP iframe -->
    <div
      class="flex-1 min-w-0 transition-all duration-300"
      :class="{ 'hidden sm:block': mobilePanelOpen }"
    >
      <iframe
        ref="iframeRef"
        src="/static/nlp_notes/index.html"
        class="w-full h-full border-0"
        title="NLP 学习笔记"
      ></iframe>
    </div>

    <!-- Right: Notes & Annotations Panel (desktop) -->
    <div
      class="hidden sm:flex flex-col border-l border-base-300 bg-base-100 transition-all duration-300 overflow-hidden"
      :class="panelOpen ? 'w-80' : 'w-10'"
    >
      <button class="btn btn-ghost btn-sm rounded-none w-full shrink-0" @click="panelOpen = !panelOpen">
        <span v-if="panelOpen" class="text-xs">收起 →</span>
        <span v-else class="text-xs">笔<br>记</span>
      </button>

      <template v-if="panelOpen">
        <!-- Tabs -->
        <div class="flex border-b border-base-200 shrink-0">
          <button
            class="flex-1 py-2 text-xs font-medium transition-colors"
            :class="activeTab === 'page' ? 'text-primary border-b-2 border-primary' : 'text-base-content/50'"
            @click="activeTab = 'page'"
          >页面笔记</button>
          <button
            class="flex-1 py-2 text-xs font-medium transition-colors"
            :class="activeTab === 'annotations' ? 'text-primary border-b-2 border-primary' : 'text-base-content/50'"
            @click="activeTab = 'annotations'"
          >批注 ({{ annotations.length }})</button>
        </div>

        <!-- Login gate -->
        <div v-if="!isLoggedIn" class="flex-1 flex flex-col items-center justify-center px-4 text-center">
          <p class="text-sm text-base-content/60 mb-3">登录后即可做笔记和批注</p>
          <button class="btn btn-sm btn-primary" @click="requireLogin">登录</button>
        </div>

        <!-- Page note tab -->
        <template v-else-if="activeTab === 'page'">
          <textarea
            v-model="noteContent"
            class="textarea textarea-bordered flex-1 rounded-none resize-none text-sm leading-relaxed"
            placeholder="整页笔记..."
          ></textarea>
          <div class="px-3 py-1.5 text-xs text-base-content/50 shrink-0 text-right">
            <span v-if="noteSaveStatus === 'saving'" class="text-warning">保存中...</span>
            <span v-else-if="noteSaveStatus === 'saved'" class="text-success">已自动保存</span>
            <span v-else-if="noteSaveStatus === 'unsaved'" class="text-error">保存失败</span>
            <span v-else>&nbsp;</span>
          </div>
        </template>

        <!-- Annotations tab -->
        <template v-else>
          <!-- Editing form -->
          <div v-if="editingAnno" class="border-b border-base-200 p-3 shrink-0">
            <div class="text-xs text-base-content/60 mb-2 p-2 bg-base-200 rounded italic">
              "{{ editingAnno.selected_text }}"
            </div>
            <textarea
              v-model="editingAnno.content"
              class="textarea textarea-bordered w-full rounded resize-none text-sm leading-relaxed"
              rows="3"
              placeholder="输入批注..."
            ></textarea>
            <div class="flex items-center justify-between mt-2">
              <span class="text-xs text-base-content/50">
                <span v-if="annoSaveStatus === 'saving'" class="text-warning">保存中...</span>
                <span v-else-if="annoSaveStatus === 'saved'" class="text-success">已保存</span>
                <span v-else-if="annoSaveStatus === 'unsaved'" class="text-error">保存失败</span>
              </span>
              <div class="flex gap-1">
                <button class="btn btn-xs btn-ghost" @click="cancelEditAnnotation">取消</button>
                <button class="btn btn-xs btn-primary" @click="saveAnnotation">
                  {{ editingAnno.id ? '更新' : '保存' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Annotation list -->
          <div class="flex-1 overflow-y-auto">
            <div v-if="!annotations.length" class="p-4 text-center text-sm text-base-content/50">
              选中页面中的文字，点击下方按钮添加批注
            </div>
            <div
              v-for="ann in annotations"
              :key="ann.id"
              class="border-b border-base-200 p-3 cursor-pointer hover:bg-base-200 transition-colors"
              :class="{ 'bg-base-200': editingAnno?.id === ann.id }"
              @click="startEditAnnotation(ann)"
            >
              <div class="text-xs text-warning italic mb-1 truncate">
                "{{ ann.selected_text }}"
              </div>
              <div class="text-sm text-base-content leading-relaxed line-clamp-3">
                {{ ann.content || '(空批注)' }}
              </div>
              <div class="flex items-center justify-between mt-1.5">
                <span class="text-xs text-base-content/40">{{ new Date(ann.updated_at).toLocaleDateString() }}</span>
                <button
                  class="btn btn-ghost btn-xs text-error"
                  @click.stop="deleteAnnotation(ann.id)"
                >删除</button>
              </div>
            </div>
          </div>

          <!-- Selected text hint -->
          <div v-if="selectedText && !editingAnno" class="shrink-0 border-t border-base-200 p-3">
            <div class="text-xs text-base-content/60 mb-2 p-2 bg-warning/10 rounded italic">
              已选中: "{{ selectedText.text.slice(0, 80) }}{{ selectedText.text.length > 80 ? '...' : '' }}"
            </div>
            <button class="btn btn-sm btn-primary w-full" @click="startNewAnnotation">
              为此文字添加批注
            </button>
          </div>
        </template>
      </template>
    </div>

    <!-- Add annotation floating button (appears when text is selected) -->
    <div
      v-if="selectedText && !editingAnno && isLoggedIn"
      class="hidden sm:block fixed bottom-8 left-1/2 -translate-x-1/2 z-40 animate-bounce"
    >
      <button class="btn btn-primary shadow-lg" @click="startNewAnnotation">
        为此文字添加批注
      </button>
    </div>

    <!-- Mobile -->
    <div class="sm:hidden">
      <button v-if="!mobilePanelOpen" class="btn btn-primary btn-sm shadow-lg fixed bottom-6 right-6 z-40" @click="mobilePanelOpen = true">
        笔记
      </button>
      <!-- Mobile selected text action -->
      <div
        v-if="selectedText && !editingAnno && isLoggedIn && !mobilePanelOpen"
        class="fixed bottom-20 left-4 right-4 z-40"
      >
        <button class="btn btn-primary btn-sm w-full shadow-lg" @click="mobilePanelOpen = true; startNewAnnotation()">
          为选中文字添加批注
        </button>
      </div>
      <div v-if="mobilePanelOpen" class="fixed inset-x-0 bottom-0 z-40 bg-base-100 rounded-t-2xl shadow-2xl" style="max-height: 60vh;">
        <div class="flex items-center justify-between px-4 py-3 border-b border-base-200">
          <span class="text-sm font-medium truncate">{{ panelTitle }}</span>
          <button class="btn btn-ghost btn-xs" @click="mobilePanelOpen = false">收起</button>
        </div>
        <div v-if="!isLoggedIn" class="flex flex-col items-center justify-center py-12 px-4 text-center">
          <p class="text-sm text-base-content/60 mb-3">登录后即可做笔记</p>
          <button class="btn btn-sm btn-primary" @click="requireLogin">登录</button>
        </div>
        <template v-else>
          <textarea v-model="noteContent" class="textarea textarea-bordered w-full rounded-none resize-none text-sm" style="height: 40vh;" placeholder="记录你的学习笔记..."></textarea>
          <div class="px-4 py-1.5 text-xs text-base-content/50 text-right">
            <span v-if="noteSaveStatus === 'saving'" class="text-warning">保存中...</span>
            <span v-else-if="noteSaveStatus === 'saved'" class="text-success">已自动保存</span>
            <span v-else>&nbsp;</span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>
