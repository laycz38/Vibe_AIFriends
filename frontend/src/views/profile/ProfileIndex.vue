<script setup>
import { reactive, ref, watch, computed } from 'vue'
import { RouterLink } from 'vue-router'
import { useUserStore } from '../../stores/user.js'
import Photo from './components/Photo.vue'

const userStore = useUserStore()
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const photoRef = ref(null)

const displayName = computed(() => userStore.user?.username || '未登录用户')

const form = reactive({
  bio: '',
})

watch(
  () => userStore.user,
  (user) => {
    form.bio = user?.bio || ''
  },
  { immediate: true },
)

async function submitProfile() {
  saving.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    const payload = { bio: form.bio }
    const newPhoto = photoRef.value?.myPhoto
    if (newPhoto && newPhoto !== userStore.user?.photo) {
      payload.photo_base64 = newPhoto
    }
    await userStore.updateProfile(payload)
    successMessage.value = '资料已更新'
  } catch (error) {
    errorMessage.value = error.response?.data?.message || error.message || '更新资料失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="flex justify-center p-6">
    <div class="card w-full max-w-lg bg-base-200 shadow-sm mt-8">
      <div class="card-body">
        <h3 class="text-lg font-bold mb-2">编辑资料</h3>
        <p class="text-sm text-base-content/60 mb-6">{{ displayName }} 的个人主页</p>

        <Photo ref="photoRef" :photo="userStore.user?.photo || ''" />

        <div class="divider my-6"></div>

        <fieldset class="fieldset">
          <legend class="fieldset-legend text-base">个人简介</legend>
          <textarea
            v-model="form.bio"
            class="textarea w-full"
            rows="5"
            placeholder="写一段你的求职方向、擅长技术、目标公司或面试准备方法..."
          ></textarea>
          <p class="fieldset-label text-xs text-base-content/50">{{ form.bio.length }} / 500</p>
        </fieldset>

        <p v-if="successMessage" class="text-sm text-success mt-2">{{ successMessage }}</p>
        <p v-if="errorMessage" class="text-sm text-error mt-2">{{ errorMessage }}</p>

        <button
          class="btn btn-neutral mt-4"
          :disabled="saving"
          @click="submitProfile"
        >
          {{ saving ? '保存中...' : '保存资料' }}
        </button>

        <div class="divider my-4"></div>

        <div class="stats stats-horizontal shadow-sm">
          <div class="stat text-center">
            <div class="stat-title text-xs">发布面经</div>
            <div class="stat-value text-xl">{{ userStore.user?.note_count || 0 }}</div>
          </div>
          <div class="stat text-center">
            <div class="stat-title text-xs">发布评论</div>
            <div class="stat-value text-xl">{{ userStore.user?.comment_count || 0 }}</div>
          </div>
          <div class="stat text-center">
            <div class="stat-title text-xs">点赞次数</div>
            <div class="stat-value text-xl">{{ userStore.user?.like_count || 0 }}</div>
          </div>
        </div>

        <RouterLink
          v-if="userStore.user"
          :to="`/user/${userStore.user.id}/`"
          class="btn btn-ghost btn-sm mt-2"
        >
          查看我的空间
        </RouterLink>
      </div>
    </div>
  </div>
</template>
