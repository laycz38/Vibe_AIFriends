<script setup>
import { reactive, ref, watch } from 'vue'
import api from '@/js/http/api.js'

const props = defineProps({
  note: {
    type: Object,
    default: null,
  },
  visible: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['close', 'updated'])

const saving = ref(false)
const errorMessage = ref('')
const dialogRef = ref(null)
const coverFile = ref(null)

const form = reactive({
  title: '',
  content: '',
  company: '',
  position: '',
  difficulty: '中等',
})

watch(() => props.visible, (val) => {
  if (val) {
    dialogRef.value?.showModal()
    if (props.note) {
      form.title = props.note.title || ''
      form.content = props.note.content || ''
      form.company = props.note.company || ''
      form.position = props.note.position || ''
      form.difficulty = props.note.difficulty || '中等'
    }
    coverFile.value = null
    errorMessage.value = ''
  }
})

function close() {
  dialogRef.value?.close()
  emit('close')
}

function onCoverChange(e) {
  coverFile.value = e.target.files?.[0] || null
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
    reader.readAsDataURL(file)
  })
}

async function submit() {
  if (!form.title.trim() || !form.content.trim()) {
    errorMessage.value = '标题和内容不能为空'
    return
  }

  saving.value = true
  errorMessage.value = ''

  try {
    const payload = {
      title: form.title.trim(),
      content: form.content.trim(),
      company: form.company.trim(),
      position: form.position.trim(),
      difficulty: form.difficulty,
    }

    if (coverFile.value) {
      payload.cover_base64 = await fileToBase64(coverFile.value)
    }

    const response = await api.put(`/api/notes/${props.note.id}/update/`, payload)
    if (response.data?.result === 'success') {
      emit('updated', response.data.note)
      close()
    } else {
      errorMessage.value = response.data?.message || '更新失败'
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.message || error.message || '更新失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <dialog ref="dialogRef" class="modal" @close="emit('close')">
    <div class="modal-box w-full max-w-lg transition-none">
      <h3 class="text-lg font-bold mb-4">编辑面经</h3>

      <div class="space-y-4">
        <fieldset class="fieldset">
          <legend class="fieldset-legend text-sm">标题</legend>
          <input v-model="form.title" type="text" class="input w-full" placeholder="面经标题" />
        </fieldset>

        <fieldset class="fieldset">
          <legend class="fieldset-legend text-sm">内容</legend>
          <textarea v-model="form.content" class="textarea w-full" rows="8" placeholder="面经内容"></textarea>
        </fieldset>

        <div class="grid grid-cols-2 gap-3">
          <fieldset class="fieldset">
            <legend class="fieldset-legend text-sm">公司</legend>
            <input v-model="form.company" type="text" class="input w-full" placeholder="公司名称" />
          </fieldset>
          <fieldset class="fieldset">
            <legend class="fieldset-legend text-sm">职位</legend>
            <input v-model="form.position" type="text" class="input w-full" placeholder="职位名称" />
          </fieldset>
        </div>

        <fieldset class="fieldset">
          <legend class="fieldset-legend text-sm">难度</legend>
          <select v-model="form.difficulty" class="select w-full">
            <option value="简单">简单</option>
            <option value="中等">中等</option>
            <option value="困难">困难</option>
          </select>
        </fieldset>

        <fieldset class="fieldset">
          <legend class="fieldset-legend text-sm">封面图片（可选）</legend>
          <input
            type="file"
            accept="image/*"
            class="file-input file-input-sm w-full"
            @change="onCoverChange"
          />
        </fieldset>
      </div>

      <p v-if="errorMessage" class="text-sm text-error mt-3">{{ errorMessage }}</p>

      <div class="modal-action">
        <button class="btn btn-ghost btn-sm" @click="close">取消</button>
        <button class="btn btn-primary btn-sm" :disabled="saving" @click="submit">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
    <form method="dialog" class="modal-backdrop">
      <button>close</button>
    </form>
  </dialog>
</template>
