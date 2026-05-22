<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { MicVAD } from '@ricky0123/vad-web'
import api from '@/js/http/api.js'
import KeyboardIcon from '@/components/icons/KeyboardIcon.vue'

const emit = defineEmits(['close', 'send', 'stop', 'error'])
const isSpeaking = ref(false)
const initError = ref('')
const loading = ref(true)

let vadInstance = null

const VAD_BASE = import.meta.env.DEV
  ? '/vad/'
  : '/static/frontend/vad/'

const startRecording = async () => {
  try {
    console.log('[VAD] Initializing with base path:', VAD_BASE)

    vadInstance = await MicVAD.new({
      model: 'v5',
      baseAssetPath: VAD_BASE,
      onSpeechStart: () => {
        console.log('[VAD] Speech started')
        isSpeaking.value = true
        emit('stop')
      },
      onSpeechEnd: (audio) => {
        console.log('[VAD] Speech ended, audio samples:', audio.length)
        isSpeaking.value = false
        const pcm16 = float32ToInt16(audio)
        sendToBackend(pcm16)
      },
      onVADMisfire: () => {
        console.log('[VAD] Misfire')
        isSpeaking.value = false
      },
      ortConfig: (ort) => {
        ort.env.logLevel = 'error'
        ort.env.wasm.wasmPaths = '/node_modules/onnxruntime-web/dist/'
      },
      positiveSpeechThreshold: 0.8,
      negativeSpeechThreshold: 0.65,
      minSpeechFrames: 5,
      redemptionFrames: 5,
    })

    loading.value = false
    await vadInstance.start()
    console.log('[VAD] Started successfully')
  } catch (e) {
    loading.value = false
    const msg = e.message || String(e)
    console.error('[VAD] Init failed:', msg)
    initError.value = msg

    if (msg.includes('NotAllowedError') || msg.includes('Permission')) {
      initError.value = '请允许麦克风权限后重试'
    } else if (msg.includes('fetch') || msg.includes('NetworkError') || msg.includes('Failed to fetch')) {
      initError.value = '语音模型加载失败，请检查网络连接'
    } else if (msg.includes('model') || msg.includes('onnx')) {
      initError.value = '语音模型文件缺失，请刷新页面重试'
    }
    emit('error', initError.value)
  }
}

const float32ToInt16 = (float32Array) => {
  const buffer = new Int16Array(float32Array.length)
  for (let i = 0; i < float32Array.length; i++) {
    let s = Math.max(-1, Math.min(1, float32Array[i]))
    buffer[i] = s < 0 ? s * 0x8000 : s * 0x7fff
  }
  return buffer.buffer
}

const sendToBackend = async (arrayBuffer) => {
  const blob = new Blob([arrayBuffer], { type: 'audio/pcm' })
  const formData = new FormData()
  formData.append('audio', blob, 'voice.pcm')

  try {
    const res = await api.post('/api/tts/asr/', formData)
    const data = res.data
    if (data.result === 'success' && data.text) {
      emit('send', null, data.text)
    } else {
      console.error('[ASR] Unexpected response:', data)
    }
  } catch (err) {
    console.error('[ASR] Request failed:', err)
    emit('error', '语音识别请求失败')
  }
}

onMounted(() => {
  startRecording()
})

onBeforeUnmount(() => {
  if (vadInstance) {
    vadInstance.destroy()
    vadInstance = null
  }
})
</script>

<template>
  <div class="absolute bottom-0 left-0 right-0 h-12 flex items-center bg-base-200 rounded-box mx-2 mb-2">
    <!-- Error state -->
    <div v-if="initError" class="text-error text-xs w-full text-center px-2">
      {{ initError }}
    </div>
    <!-- Loading state -->
    <div v-else-if="loading" class="text-base-content/50 text-sm w-full text-center">
      正在初始化语音模型...
    </div>
    <!-- Speaking state: waveform animation -->
    <div v-else-if="isSpeaking" class="flex items-center justify-center gap-0.5 h-6 flex-1 px-4">
      <div
        v-for="i in 32" :key="i"
        class="w-0.5 bg-primary rounded-full animate-wave"
        :style="{ animationDelay: `${i * 0.1}s` }"
      ></div>
    </div>
    <!-- Listening state -->
    <div v-else class="text-base-content/50 text-sm w-full text-center">
      正在聆听...
    </div>
    <button v-if="!loading" class="btn btn-ghost btn-xs mr-1" @click="emit('close')">
      <KeyboardIcon />
    </button>
  </div>
</template>

<style scoped>
.animate-wave {
  height: 4px;
  animation: wave-animation 0.6s ease-in-out infinite alternate;
}

@keyframes wave-animation {
  0% { height: 4px; opacity: 0.3; }
  100% { height: 20px; opacity: 1; }
}
</style>
