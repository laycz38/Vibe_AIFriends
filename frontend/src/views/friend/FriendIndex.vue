<script setup>
import { computed, onMounted, onBeforeUnmount, ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/js/http/api.js'
import { useUserStore } from '@/stores/user.js'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const BASE_URL = import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''

// -- state --
const messages = ref([])
const inputText = ref('')
const sending = ref(false)
const chatContainer = ref(null)
const speakingIndex = ref(-1)
const currentAudio = ref(null) // HTMLAudioElement for Aliyun TTS playback
const notes = ref([])
const sessions = ref([])
const loadedSessionId = ref(null)
const sessionId = ref(null) // current auto-save session id
const voiceGender = ref(localStorage.getItem('tts_gender') || 'female')
const showSaveToast = ref(false)
const showCleanWarning = ref(false)
const cleanDismissed = ref(false)
const showTtsError = ref('') // error message, falsy when ok
const ttsFallbackUsed = ref(false) // brief toast when CosyVoice falls back

// -- computed --
const interviewNoteId = computed(() => {
  const raw = route.query.interview
  return raw ? Number(raw) : null
})
const currentNote = computed(() => {
  if (!interviewNoteId.value) return null
  return notes.value.find((n) => n.id === interviewNoteId.value) || null
})
const isInterviewMode = computed(() => !!currentNote.value)
const isReadOnly = computed(() => loadedSessionId.value !== null)
const draftKey = computed(() => {
  if (isInterviewMode.value) return `chat_draft_note_${interviewNoteId.value}`
  return 'chat_draft_free'
})
const hasMessages = computed(() => messages.value.length > 1)

// message total char count
const totalChars = computed(() => {
  return messages.value.reduce((sum, m) => sum + (m.content || '').length, 0)
})

// text length warning
const charWarningLevel = computed(() => {
  if (cleanDismissed.value) return null
  if (totalChars.value > 6000) return 'danger'
  if (totalChars.value > 4000) return 'warn'
  return null
})

async function scrollToBottom() {
  await nextTick()
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

function getWelcomeMessage() {
  if (currentNote.value) {
    return `你好！我来模拟一下「${currentNote.value.title}」（${currentNote.value.company} · ${currentNote.value.position}）的面试，准备好了就开始吧，先简单介绍一下自己~`
  }
  return '你好！我是 AI 面试助手，可以帮你解答面试相关的问题。选择一篇面经笔记可以开始模拟面试，也可以直接向我提问。'
}

function setGender(gender) {
  voiceGender.value = gender
  localStorage.setItem('tts_gender', gender)
}

// MediaSource refs for streaming playback
const mediaSourceRef = ref(null)
const sourceBufferRef = ref(null)
const streamAbortRef = ref(null)

// Browser SpeechSynthesis fallback (used when Aliyun TTS is unavailable)
function speakFallback(index, text) {
  if (typeof speechSynthesis === 'undefined') return false
  try {
    speechSynthesis.cancel()
    const utterance = new SpeechSynthesisUtterance(text)
    utterance.lang = 'zh-CN'
    utterance.rate = 0.88
    utterance.pitch = 1.05
    utterance.onend = () => { speakingIndex.value = -1 }
    utterance.onerror = () => { speakingIndex.value = -1 }
    speechSynthesis.speak(utterance)
    return true
  } catch {
    return false
  }
}

async function speak(index, text) {
  // Toggle off if clicking the same message
  if (speakingIndex.value === index && currentAudio.value) {
    currentAudio.value.pause()
    currentAudio.value = null
    speakingIndex.value = -1
    return
  }

  // Stop previous playback
  if (currentAudio.value) {
    currentAudio.value.pause()
    currentAudio.value = null
  }
  if (streamAbortRef.value) {
    streamAbortRef.value.abort()
    streamAbortRef.value = null
  }
  speechSynthesis.cancel()
  speakingIndex.value = -1

  speakingIndex.value = index

  // Try streaming TTS via MediaSource (first chunk plays in ~0.5s)
  try {
    const abortController = new AbortController()
    streamAbortRef.value = abortController

    const resp = await fetch(`${BASE_URL}/api/tts/stream/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${userStore.accessToken}`,
      },
      body: JSON.stringify({ text, voice: voiceGender.value }),
      signal: abortController.signal,
    })

    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}))
      throw new Error(errData.message || `HTTP ${resp.status}`)
    }

    // Setup MediaSource for progressive MP3 playback
    const ms = new MediaSource()
    mediaSourceRef.value = ms
    const audioUrl = URL.createObjectURL(ms)
    const audio = new Audio(audioUrl)
    currentAudio.value = audio

    const chunks = []
    let sourceBuffer = null
    let msClosed = false

    const cleanup = () => {
      if (!msClosed) {
        msClosed = true
        try { URL.revokeObjectURL(audioUrl) } catch {}
      }
      speakingIndex.value = -1
      currentAudio.value = null
      streamAbortRef.value = null
    }

    audio.onended = cleanup
    audio.onerror = cleanup

    await new Promise((resolve, reject) => {
      ms.addEventListener('sourceopen', () => {
        try {
          sourceBuffer = ms.addSourceBuffer('audio/mpeg')
          sourceBuffer.mode = 'sequence'

          sourceBuffer.addEventListener('updateend', () => {
            if (chunks.length > 0 && !sourceBuffer.updating) {
              sourceBuffer.appendBuffer(chunks.shift())
            }
          })

          // Append any chunk that arrived before sourceopen
          if (chunks.length > 0 && !sourceBuffer.updating) {
            sourceBuffer.appendBuffer(chunks.shift())
          }
        } catch (e) {
          reject(e)
        }
      })

      // Read stream chunks
      const reader = resp.body.getReader()
      function pushChunk(data) {
        chunks.push(data)
        if (sourceBuffer && !sourceBuffer.updating) {
          sourceBuffer.appendBuffer(chunks.shift())
        }
        // Start playing as soon as first chunk is buffered
        if (audio.paused && audio.readyState < 2) {
          audio.play().catch(() => {})
        }
      }

      function readLoop() {
        reader.read().then(({ done, value }) => {
          if (done) {
            if (sourceBuffer && !sourceBuffer.updating && ms.readyState === 'open') {
              try { ms.endOfStream() } catch {}
            }
            resolve()
            return
          }
          pushChunk(value)
          readLoop()
        }).catch((err) => {
          if (err.name === 'AbortError') { resolve(); return }
          reject(err)
        })
      }
      readLoop()
    })
  } catch (err) {
    if (err.name === 'AbortError') return

    console.warn('CosyVoice stream 失败，回退非流式:', err)

    // Fallback 1: non-streaming TTS endpoint (still SDK-based, faster than REST)
    try {
      const { data } = await api.post('/api/tts/synthesize/', {
        text,
        voice: voiceGender.value,
      }, { timeout: 30000 })

      if (data.result === 'success' && data.audio) {
        const byteChars = atob(data.audio)
        const len = byteChars.length
        const buf = new ArrayBuffer(len)
        const view = new Uint8Array(buf)
        for (let i = 0; i < len; i++) view[i] = byteChars.charCodeAt(i)
        const blob = new Blob([buf], { type: 'audio/mp3' })
        const url = URL.createObjectURL(blob)
        const audio = new Audio(url)
        currentAudio.value = audio
        audio.onended = () => {
          speakingIndex.value = -1
          currentAudio.value = null
          URL.revokeObjectURL(url)
        }
        audio.onerror = () => {
          speakingIndex.value = -1
          currentAudio.value = null
          URL.revokeObjectURL(url)
        }
        audio.play().catch(() => {
          speakingIndex.value = -1
          currentAudio.value = null
          URL.revokeObjectURL(url)
        })
        return
      }
      throw new Error(data.message || 'no audio')
    } catch (err2) {
      console.warn('CosyVoice 非流式也失败:', err2)
      showTtsError.value = err2.message
      setTimeout(() => { showTtsError.value = '' }, 5000)
      ttsFallbackUsed.value = true
      setTimeout(() => { ttsFallbackUsed.value = false }, 3000)
      if (!speakFallback(index, text)) {
        speakingIndex.value = -1
        showTtsError.value = '浏览器语音也不可用'
        setTimeout(() => { showTtsError.value = '' }, 4000)
      }
    }
  }
}

// -- localStorage draft --
function saveDraft() {
  if (messages.value.length > 1) {
    localStorage.setItem(draftKey.value, JSON.stringify(messages.value))
  }
}

function loadDraft() {
  const raw = localStorage.getItem(draftKey.value)
  if (raw) {
    try {
      const parsed = JSON.parse(raw)
      if (parsed.length) messages.value = parsed
      return true
    } catch { /* ignore */ }
  }
  return false
}

function clearDraft() {
  localStorage.removeItem(draftKey.value)
}

// -- auto-save to backend --
async function autoSaveSession() {
  if (messages.value.length <= 1) return
  const payload = {
    messages: messages.value.map(({ role, content }) => ({ role, content })),
    note_id: interviewNoteId.value || null,
    title: currentNote.value
      ? `${currentNote.value.company} - ${currentNote.value.title} 面试`
      : '自由对话',
  }
  if (sessionId.value) payload.session_id = sessionId.value
  try {
    const { data } = await api.post('/api/chat/sessions/save/', payload)
    if (data.result === 'success') {
      sessionId.value = data.session.id
      localStorage.setItem('chat_session_id', String(data.session.id))
      loadSessions()
    }
  } catch { /* silent */ }
}

async function loadAutoSession() {
  const stored = localStorage.getItem('chat_session_id')
  if (stored) {
    try {
      const sid = Number(stored)
      const { data } = await api.get(`/api/chat/sessions/${sid}/`)
      if (data.result === 'success' && data.session.messages.length > 0) {
        messages.value = data.session.messages
        sessionId.value = sid
        loadedSessionId.value = sid // show as read-only? No, allow continuing
        loadedSessionId.value = null // allow continuing
        return true
      }
    } catch { /* not found or expired */ }
  }
  return false
}

// -- send message --
async function send() {
  const text = inputText.value.trim()
  if (!text || sending.value || isReadOnly.value) return

  messages.value.push({ role: 'user', content: text })
  inputText.value = ''
  sending.value = true
  await scrollToBottom()

  const payload = {
    messages: messages.value.map(({ role, content }) => ({ role, content })),
  }
  if (isInterviewMode.value) {
    payload.note_id = interviewNoteId.value
  }
  const url = isInterviewMode.value ? '/api/chat/interview/' : '/api/chat/send/'

  try {
    const { data } = await api.post(url, payload)
    if (data.result === 'success') {
      messages.value.push(data.message)
      if (data.note) {
        const existing = notes.value.find((n) => n.id === data.note.id)
        if (!existing) notes.value.push(data.note)
      }
      // auto-save to backend
      await autoSaveSession()
      // auto-play in interview mode
      if (isInterviewMode.value) {
        setTimeout(() => speak(messages.value.length - 1, data.message.content), 300)
      }
    } else {
      messages.value.push({ role: 'assistant', content: `出错了：${data.message || '未知错误'}` })
    }
  } catch (e) {
    messages.value.push({
      role: 'assistant',
      content: `请求失败：${e.response?.data?.message || e.message || '网络错误'}`,
    })
  } finally {
    sending.value = false
    await scrollToBottom()
  }
}

function handleKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    send()
  }
}

// -- clear conversation --
function clearConversation() {
  if (messages.value.length <= 1) return
  saveDraft() // backup before clear
  messages.value = [{ role: 'assistant', content: getWelcomeMessage() }]
  clearDraft()
  sessionId.value = null
  localStorage.removeItem('chat_session_id')
  cleanDismissed.value = false
  showCleanWarning.value = false
  if (streamAbortRef.value) {
    streamAbortRef.value.abort()
    streamAbortRef.value = null
  }
  if (currentAudio.value) {
    currentAudio.value.pause()
    currentAudio.value = null
  }
  if (typeof speechSynthesis !== 'undefined') speechSynthesis.cancel()
  speakingIndex.value = -1
}

// -- notes & sessions --
async function selectNote(noteId) {
  router.push({ name: 'friend', query: noteId ? { interview: noteId } : {} })
}

function exitInterview() {
  router.push({ name: 'friend' })
}

async function loadNotes() {
  try {
    const { data } = await api.get('/api/notes/')
    if (data.result === 'success') notes.value = data.notes
  } catch { /* silent */ }
}

async function loadSessions() {
  try {
    const { data } = await api.get('/api/chat/sessions/')
    if (data.result === 'success') sessions.value = data.sessions
  } catch { /* silent */ }
}

async function saveSession() {
  if (!hasMessages.value) return
  await autoSaveSession()
  showSaveToast.value = true
  setTimeout(() => { showSaveToast.value = false }, 2000)
}

async function loadSession(sid) {
  if (sid === 'back') {
    loadedSessionId.value = null
    sessionId.value = Number(localStorage.getItem('chat_session_id')) || null
    const restored = await loadAutoSession()
    if (!restored) {
      const found = loadDraft()
      if (!found) messages.value = [{ role: 'assistant', content: getWelcomeMessage() }]
    }
    await scrollToBottom()
    return
  }
  if (!sid) return
  try {
    const { data } = await api.get(`/api/chat/sessions/${sid}/`)
    if (data.result === 'success') {
      messages.value = data.session.messages
      loadedSessionId.value = sid
      if (data.session.note_id) {
        router.replace({ name: 'friend', query: { interview: data.session.note_id } })
      }
      await scrollToBottom()
    }
  } catch { /* silent */ }
}

async function deleteSession(sid) {
  try {
    await api.delete(`/api/chat/sessions/${sid}/delete/`)
    sessions.value = sessions.value.filter((s) => s.id !== sid)
    if (loadedSessionId.value === sid || sessionId.value === sid) {
      loadedSessionId.value = null
      sessionId.value = null
      localStorage.removeItem('chat_session_id')
      messages.value = [{ role: 'assistant', content: getWelcomeMessage() }]
    }
  } catch { /* silent */ }
}

function formatTime(iso) {
  const d = new Date(iso)
  const pad = (n) => String(n).padStart(2, '0')
  return `${d.getMonth() + 1}/${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// -- life cycle --
watch(interviewNoteId, (newId, oldId) => {
  if (newId !== oldId) {
    loadedSessionId.value = null
    sessionId.value = null
    localStorage.removeItem('chat_session_id')
    const found = loadDraft()
    if (!found) messages.value = [{ role: 'assistant', content: getWelcomeMessage() }]
    scrollToBottom()
  }
})

onMounted(() => {
  loadNotes()
  loadSessions()

  const restored = loadAutoSession()
  if (!restored) {
    const found = loadDraft()
    if (!found) messages.value = [{ role: 'assistant', content: getWelcomeMessage() }]
  }
  scrollToBottom()
})

onBeforeUnmount(() => {
  if (streamAbortRef.value) {
    streamAbortRef.value.abort()
    streamAbortRef.value = null
  }
  if (currentAudio.value) {
    currentAudio.value.pause()
    currentAudio.value = null
  }
  if (typeof speechSynthesis !== 'undefined') speechSynthesis.cancel()
})
</script>

<template>
  <div class="flex flex-col h-[calc(100dvh-4rem)] max-w-3xl mx-auto w-full">
    <!-- Header -->
    <div class="px-3 md:px-6 py-2 md:py-3 border-b border-base-300 shrink-0 space-y-2">
      <div class="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-4">
        <div class="min-w-0 flex-1">
          <h1 class="text-lg md:text-xl font-bold truncate pr-2">
            <template v-if="loadedSessionId">查看记录</template>
            <template v-else>{{ isInterviewMode ? '模拟面试' : 'AI 面试助手' }}</template>
          </h1>
          <p class="text-xs md:text-sm text-base-content/60 truncate">
            <template v-if="loadedSessionId">只读回放，不可继续对话</template>
            <template v-else-if="isInterviewMode">
              正在面试：{{ currentNote.title }}（{{ currentNote.company }} · {{ currentNote.position }}）
              <button class="link link-primary text-xs ml-2" @click="exitInterview">退出面试</button>
            </template>
            <template v-else>基于 DeepSeek 大模型，自动保存到云端</template>
          </p>
        </div>

        <div class="flex items-center gap-1 md:gap-2 flex-wrap justify-end">
          <!-- Voice gender selector -->
          <div class="join join-xs">
            <button
              class="btn btn-xs join-item"
              :class="voiceGender === 'female' ? 'btn-active' : 'btn-ghost'"
              @click="setGender('female')"
            >
              女生
            </button>
            <button
              class="btn btn-xs join-item"
              :class="voiceGender === 'male' ? 'btn-active' : 'btn-ghost'"
              @click="setGender('male')"
            >
              男生
            </button>
          </div>

          <!-- Note selector -->
          <select
            class="select select-bordered select-xs w-24 md:w-32"
            :disabled="!!loadedSessionId"
            @change="selectNote(($event.target).value)"
            :value="interviewNoteId || ''"
          >
            <option value="">自由对话</option>
            <option v-for="n in notes" :key="n.id" :value="n.id">{{ n.company }} - {{ n.title }}</option>
          </select>

          <!-- History dropdown -->
          <div class="dropdown dropdown-end">
            <button tabindex="0" class="btn btn-ghost btn-xs px-1 md:px-2">
              记录
            </button>
            <ul tabindex="0" class="dropdown-content menu bg-base-200 rounded-box z-50 w-60 md:w-72 p-2 shadow mt-1 max-h-72 overflow-y-auto flex-nowrap">
              <li v-if="sessions.length === 0" class="text-xs text-base-content/40 px-3 py-2">暂无记录</li>
              <li
                v-for="s in sessions"
                :key="s.id"
                class="flex flex-row items-center"
                :class="{ 'bg-primary/10 rounded': loadedSessionId === s.id }"
              >
                <a class="text-sm flex-1 min-w-0" @click="loadSession(s.id)">
                  <div class="truncate">{{ s.title }}</div>
                  <div class="text-xs text-base-content/40">{{ formatTime(s.updated_at) }}</div>
                </a>
                <button class="btn btn-ghost btn-xs text-error shrink-0" @click="deleteSession(s.id)">×</button>
              </li>
            </ul>
          </div>

          <!-- Save button -->
          <template v-if="!loadedSessionId">
            <button class="btn btn-outline btn-xs" :disabled="!hasMessages" @click="saveSession">
              保存
            </button>
            <button
              v-if="hasMessages"
              class="btn btn-ghost btn-xs text-warning px-1 md:px-2"
              @click="clearConversation"
            >
              清空
            </button>
          </template>
          <button v-else class="btn btn-outline btn-xs" @click="loadSession('back')">
            返回
          </button>
        </div>
      </div>

      <!-- Save toast -->
      <div v-if="showSaveToast" class="toast toast-end">
        <div class="alert alert-success text-sm py-1">已保存记录</div>
      </div>
      <!-- TTS fallback toast (CosyVoice → SpeechSynthesis) -->
      <div v-if="ttsFallbackUsed" class="toast toast-end">
        <div class="alert alert-info text-sm py-1">
          已回退到浏览器语音（配置 DASHSCOPE_API_KEY 即可启用 CosyVoice）
        </div>
      </div>
      <!-- TTS error toast -->
      <div v-if="showTtsError" class="toast toast-end">
        <div class="alert alert-warning text-sm py-1 max-w-sm break-words">
          CosyVoice 失败: {{ showTtsError }}
        </div>
      </div>
    </div>

    <!-- Char length warning -->
    <div
      v-if="charWarningLevel"
      class="px-3 md:px-6 py-2 text-sm flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2"
      :class="charWarningLevel === 'danger' ? 'bg-error/10 text-error' : 'bg-warning/10 text-warning'"
    >
      <span>
        {{ charWarningLevel === 'danger'
          ? '对话内容过长（超过 6000 字），可能影响性能和效果，建议清空并保存。'
          : '对话内容较长（超过 4000 字），建议保存记录后清空，以保持体验。' }}
      </span>
      <div class="flex gap-2 shrink-0">
        <button class="btn btn-xs" :class="charWarningLevel === 'danger' ? 'btn-error' : 'btn-warning'" @click="clearConversation">
          清空并保存
        </button>
        <button class="btn btn-ghost btn-xs" @click="cleanDismissed = true">知道了</button>
      </div>
    </div>

    <!-- Messages -->
    <div ref="chatContainer" class="flex-1 overflow-y-auto px-3 md:px-6 py-2 md:py-4 space-y-3 md:space-y-4">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        class="chat"
        :class="msg.role === 'user' ? 'chat-end' : 'chat-start'"
      >
        <div class="chat-image avatar">
          <div class="w-8 md:w-10 rounded-full">
            <span
              class="flex items-center justify-center w-full h-full text-white text-xs md:text-sm font-medium"
              :class="msg.role === 'user' ? 'bg-primary' : 'bg-secondary'"
            >
              {{ msg.role === 'user' ? '我' : (isInterviewMode ? '官' : 'AI') }}
            </span>
          </div>
        </div>
        <div
          class="chat-bubble text-sm md:text-base max-w-[85vw] md:max-w-none"
          :class="msg.role === 'user' ? 'chat-bubble-primary' : ''"
        >
          {{ msg.content }}
        </div>
        <div v-if="msg.role === 'assistant'" class="chat-footer mt-1">
          <button
            class="btn btn-ghost btn-xs gap-1"
            @click="speak(i, msg.content)"
          >
            <svg
              v-if="speakingIndex !== i"
              class="size-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" />
            </svg>
            <svg
              v-else
              class="size-3.5"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
              <line x1="9" y1="9" x2="15" y2="15" />
              <line x1="15" y1="9" x2="9" y2="15" />
            </svg>
            <span class="text-xs md:text-sm">{{ speakingIndex === i ? '停止' : '朗读' }}</span>
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="sending" class="chat chat-start">
        <div class="chat-image avatar">
          <div class="w-8 md:w-10 rounded-full">
            <span class="flex items-center justify-center w-full h-full bg-secondary text-white text-xs md:text-sm font-medium">
              {{ isInterviewMode ? '官' : 'AI' }}
            </span>
          </div>
        </div>
        <div class="chat-bubble">
          <span class="loading loading-dots loading-sm"></span>
        </div>
      </div>
    </div>

    <!-- Input -->
    <div class="px-3 md:px-6 py-2 md:py-4 border-t border-base-300 shrink-0">
      <div v-if="isReadOnly" class="text-center text-xs md:text-sm text-base-content/40 py-2">
        这是已保存的记录，只读回放。点击"返回"继续聊天。
      </div>
      <div v-else class="flex gap-2">
        <input
          v-model="inputText"
          type="text"
          :placeholder="isInterviewMode ? '输入你的回答...' : '输入你的问题...'"
          class="input input-bordered flex-1 min-w-0 text-sm md:text-base"
          :disabled="sending"
          @keydown="handleKeydown"
        />
        <button
          class="btn btn-primary btn-sm md:btn-md"
          :disabled="!inputText.trim() || sending"
          @click="send"
        >
          发送
        </button>
      </div>
    </div>
  </div>
</template>
