<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { useUserStore } from '../../stores/user.js'

const userStore = useUserStore()
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')
const avatarFile = ref(null)
const avatarPreview = ref('')

const displayName = computed(() => userStore.user?.username || '未登录用户')
const profileBio = computed(() => userStore.user?.bio?.trim() || '还没有填写个人简介')

const form = reactive({
  bio: '',
})

watch(
  () => userStore.user,
  (user) => {
    form.bio = user?.bio || ''
    avatarPreview.value = user?.photo || ''
  },
  { immediate: true },
)

function handleAvatarChange(event) {
  const file = event.target.files?.[0] || null
  avatarFile.value = file

  if (file) {
    avatarPreview.value = URL.createObjectURL(file)
  } else {
    avatarPreview.value = userStore.user?.photo || ''
  }
}

async function submitProfile() {
  saving.value = true
  successMessage.value = ''
  errorMessage.value = ''

  try {
    const formData = new FormData()
    formData.append('bio', form.bio)
    if (avatarFile.value) {
      formData.append('photo', avatarFile.value)
    }
    await userStore.updateProfile(formData)
    avatarFile.value = null
    avatarPreview.value = userStore.user?.photo || ''
    successMessage.value = '资料已更新'
  } catch (error) {
    errorMessage.value = error.response?.data?.message || error.message || '更新资料失败'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <section class="p-6">
    <div class="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[360px_minmax(0,1fr)]">
      <div class="rounded-[32px] bg-white p-8 shadow-sm">
        <p class="mb-2 text-sm font-medium text-indigo-500">Profile</p>
        <h1 class="text-3xl font-bold text-gray-900">我的主页</h1>
        <p class="mt-2 text-sm text-gray-500">当前账号：{{ displayName }}</p>

        <div class="mt-8 flex flex-col items-center rounded-[28px] bg-[#fafafa] p-6 text-center">
          <div class="flex h-28 w-28 items-center justify-center overflow-hidden rounded-full bg-indigo-100 text-3xl font-semibold text-indigo-700">
            <img
              v-if="avatarPreview"
              :src="avatarPreview"
              alt="avatar"
              class="h-full w-full object-cover"
            />
            <span v-else>{{ displayName.slice(0, 1).toUpperCase() }}</span>
          </div>
          <h2 class="mt-4 text-xl font-semibold text-gray-900">{{ displayName }}</h2>
          <p class="mt-2 text-sm leading-6 text-gray-500">{{ profileBio }}</p>
        </div>

        <div class="mt-6 grid gap-4">
          <div class="rounded-2xl bg-gray-50 p-5">
            <p class="text-sm text-gray-500 mb-1">发布面经</p>
            <p class="text-2xl font-bold text-gray-900">{{ userStore.user?.note_count || 0 }}</p>
          </div>
          <div class="rounded-2xl bg-gray-50 p-5">
            <p class="text-sm text-gray-500 mb-1">发布评论</p>
            <p class="text-2xl font-bold text-gray-900">{{ userStore.user?.comment_count || 0 }}</p>
          </div>
          <div class="rounded-2xl bg-gray-50 p-5">
            <p class="text-sm text-gray-500 mb-1">点赞次数</p>
            <p class="text-2xl font-bold text-gray-900">{{ userStore.user?.like_count || 0 }}</p>
          </div>
        </div>

        <RouterLink
          :to="userStore.user ? `/user/${userStore.user.id}/` : '/user/account/login/'"
          class="mt-6 inline-flex w-full items-center justify-center rounded-2xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
        >
          {{ userStore.user ? '查看我的空间' : '去登录' }}
        </RouterLink>
      </div>

      <div class="rounded-[32px] bg-white p-8 shadow-sm">
        <div class="flex items-center justify-between gap-4">
          <div>
            <h2 class="text-2xl font-bold text-gray-900">编辑资料</h2>
            <p class="mt-2 text-sm text-gray-500">头像和简介都会保存到后端数据库，右上角头像菜单会实时显示最新资料。</p>
          </div>
        </div>

        <form class="mt-8 space-y-6" @submit.prevent="submitProfile">
          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">头像</label>
            <input
              type="file"
              accept="image/*"
              class="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none file:mr-4 file:rounded-full file:border-0 file:bg-indigo-50 file:px-4 file:py-2 file:text-sm file:font-medium file:text-indigo-600 hover:file:bg-indigo-100"
              @change="handleAvatarChange"
            />
          </div>

          <div>
            <label class="mb-2 block text-sm font-medium text-gray-700">个人简介</label>
            <textarea
              v-model="form.bio"
              class="min-h-[180px] w-full rounded-[24px] border border-gray-200 px-4 py-3 text-sm leading-7 outline-none focus:border-indigo-500"
              placeholder="写一段你的求职方向、擅长技术、目标公司或面试准备方法..."
            ></textarea>
          </div>

          <p v-if="successMessage" class="text-sm text-green-600">{{ successMessage }}</p>
          <p v-if="errorMessage" class="text-sm text-red-500">{{ errorMessage }}</p>

          <button
            class="rounded-2xl bg-indigo-600 px-6 py-3 text-sm font-medium text-white hover:bg-indigo-700 transition-colors disabled:cursor-not-allowed disabled:opacity-60"
            :disabled="saving"
          >
            {{ saving ? '保存中...' : '保存资料' }}
          </button>
        </form>
      </div>
    </div>
  </section>
</template>
