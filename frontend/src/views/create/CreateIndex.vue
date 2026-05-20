<script setup>
import { onBeforeUnmount, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/js/http/api.js'

const router = useRouter()
const loading = ref(false)
const errorMessage = ref('')
const coverFile = ref(null)
const coverPreviewUrl = ref('')

const form = reactive({
  title: '',
  company: '',
  position: '',
  difficulty: '中等',
  content: '',
})

function updateCoverPreview(file) {
  if (coverPreviewUrl.value) {
    URL.revokeObjectURL(coverPreviewUrl.value)
    coverPreviewUrl.value = ''
  }

  if (file) {
    coverPreviewUrl.value = URL.createObjectURL(file)
  }
}

function handleCoverChange(event) {
  const file = event.target.files?.[0] || null
  coverFile.value = file
  updateCoverPreview(file)
}

async function submitNote() {
  loading.value = true
  errorMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('company', form.company)
    formData.append('position', form.position)
    formData.append('difficulty', form.difficulty)
    formData.append('content', form.content)
    if (coverFile.value) {
      formData.append('cover', coverFile.value)
    }

    await api.post('/api/notes/create/', formData)
    router.push('/')
  } catch (error) {
    errorMessage.value = error.response?.data?.message || '发布失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

onBeforeUnmount(() => {
  if (coverPreviewUrl.value) {
    URL.revokeObjectURL(coverPreviewUrl.value)
  }
})
</script>

<template>
  <section class="p-6">
    <div class="max-w-3xl mx-auto bg-white rounded-3xl border border-gray-100 p-8 shadow-sm">
      <p class="text-sm text-indigo-500 font-medium mb-2">Create Interview Note</p>
      <h1 class="text-3xl font-bold text-gray-900 mb-6">发布面经</h1>
      <form class="space-y-4" @submit.prevent="submitNote">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">面经标题</label>
          <input
            v-model="form.title"
            class="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:border-indigo-500"
            placeholder="例如：字节跳动后端三面面经总结"
          />
        </div>
        <div class="grid gap-4 md:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">公司</label>
            <input
              v-model="form.company"
              class="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:border-indigo-500"
              placeholder="例如：字节跳动"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">岗位</label>
            <input
              v-model="form.position"
              class="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:border-indigo-500"
              placeholder="例如：后端开发"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">难度</label>
          <select
            v-model="form.difficulty"
            class="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:border-indigo-500"
          >
            <option value="简单">简单</option>
            <option value="中等">中等</option>
            <option value="困难">困难</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">上传封面</label>
          <input
            type="file"
            accept="image/*"
            class="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none file:mr-4 file:rounded-full file:border-0 file:bg-indigo-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-indigo-600 hover:file:bg-indigo-100"
            @change="handleCoverChange"
          />
          <p class="mt-2 text-xs text-gray-400">
            支持本地图片上传；如果不上传，首页会显示默认封面占位样式。
          </p>
          <div
            v-if="coverPreviewUrl"
            class="mt-4 overflow-hidden rounded-2xl border border-gray-200 bg-gray-50"
          >
            <img
              :src="coverPreviewUrl"
              alt="封面预览"
              class="h-64 w-full object-cover"
            />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">面经内容</label>
          <textarea
            v-model="form.content"
            class="w-full min-h-[220px] rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:border-indigo-500"
            placeholder="记录你的面试流程、题目和复盘..."
          ></textarea>
        </div>
        <p v-if="errorMessage" class="text-sm text-red-500">
          {{ errorMessage }}
        </p>
        <button
          class="rounded-2xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white hover:bg-indigo-700 transition-colors disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="loading"
        >
          {{ loading ? '发布中...' : '提交面经' }}
        </button>
      </form>
    </div>
  </section>
</template>
