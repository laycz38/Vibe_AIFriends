<script setup>
import { ref, watch, onBeforeUnmount } from 'vue'
import Croppie from 'croppie'
import 'croppie/croppie.css'
import CameraIcon from './icon/CameraIcon.vue'

const props = defineProps({
  photo: { type: String, default: '' },
})

const myPhoto = ref(props.photo)
const fileInput = ref(null)
const modalRef = ref(null)
const croppieEl = ref(null)
let croppie = null

watch(() => props.photo, (val) => {
  myPhoto.value = val
})

function triggerFileInput() {
  fileInput.value?.click()
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    openModal(reader.result)
  }
  reader.readAsDataURL(file)
}

function openModal(src) {
  modalRef.value?.showModal()
  setTimeout(() => {
    if (croppie) croppie.destroy()
    croppie = new Croppie(croppieEl.value, {
      viewport: { width: 200, height: 200, type: 'square' },
      boundary: { width: 300, height: 300 },
      enableOrientation: true,
      enforceBoundary: true,
    })
    croppie.bind({ url: src })
  }, 120)
}

async function crop() {
  if (!croppie) return
  const result = await croppie.result({ type: 'base64', size: 'viewport' })
  myPhoto.value = result
  closeModal()
}

function closeModal() {
  modalRef.value?.close()
}

onBeforeUnmount(() => {
  if (croppie) croppie.destroy()
})

defineExpose({ myPhoto })
</script>

<template>
  <div class="flex justify-center">
    <div class="avatar relative">
      <div class="w-28 rounded-full cursor-pointer" @click="triggerFileInput">
        <img v-if="myPhoto" :src="myPhoto" alt="avatar" />
        <div v-else class="flex h-full w-full items-center justify-center bg-neutral text-neutral-content text-3xl font-bold">
          ?
        </div>
      </div>
      <div
        class="absolute left-0 top-0 w-28 h-28 flex justify-center items-center bg-black/20 rounded-full cursor-pointer transition-opacity hover:bg-black/40"
        @click="triggerFileInput"
      >
        <CameraIcon />
      </div>
    </div>

    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      class="hidden"
      @change="onFileChange"
    />

    <dialog ref="modalRef" class="modal">
      <div class="modal-box transition-none">
        <h3 class="text-lg font-bold mb-4">裁剪头像</h3>
        <div ref="croppieEl" class="flex justify-center"></div>
        <div class="modal-action">
          <button class="btn btn-sm btn-ghost" @click="closeModal">取消</button>
          <button class="btn btn-sm btn-primary" @click="crop">确定</button>
        </div>
      </div>
      <form method="dialog" class="modal-backdrop">
        <button>close</button>
      </form>
    </dialog>
  </div>
</template>
