<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { MicVAD } from '@ricky0123/vad-web'
import api from '@/js/http/api.js'
import KeyboardIcon from '@/components/icons/KeyboardIcon.vue'

const emit = defineEmits(['close', 'send', 'stop'])
const isSpeaking = ref(false)

let vadInstance = null

const VAD_BASE = import.meta.env.DEV
  ? '/vad/'
  : '/static/frontend/vad/'

const startRecording = async () => {
  try {
    vadInstance = await MicVAD.new({
      baseAssetPath: VAD_BASE,
      onSpeechStart: () => {
        isSpeaking.value = true
        emit('stop')
      },
      onSpeechEnd: (audio) => {
        isSpeaking.value = false
        const pcm16 = float32ToInt16(audio)
        sendToBackend(pcm16)
      },
      ortConfig: (ort) => {
        ort.env.wasm.wasmPaths = VAD_BASE
        ort.env.logLevel = 'error'
      },
      positiveSpeechThreshold: 0.8,
      negativeSpeechThreshold: 0.65,
      minSpeechFrames: 5,
      redemptionFrames: 5,
    })

    await vadInstance.start()
  } catch (e) {
    console.error('VAD 初始化失败:', e)
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
    }
  } catch (err) {
    console.error('ASR 请求失败:', err)
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
    <div v-if="isSpeaking" class="flex items-center justify-center gap-0.5 h-6 flex-1 px-4">
      <div
        v-for="i in 32" :key="i"
        class="w-0.5 bg-primary rounded-full animate-wave"
        :style="{ animationDelay: `${i * 0.1}s` }"
      ></div>
    </div>
    <div v-else class="text-base-content/50 text-sm w-full text-center">
      正在聆听...
    </div>
    <button class="btn btn-ghost btn-xs mr-1" @click="emit('close')">
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
