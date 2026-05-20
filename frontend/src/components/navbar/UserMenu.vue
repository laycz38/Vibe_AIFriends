<script setup>
import { computed } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user.js'

const router = useRouter()
const userStore = useUserStore()

const avatarText = computed(() => {
  if (!userStore.user?.username) return 'AI'
  return userStore.user.username.slice(0, 1).toUpperCase()
})

const bioText = computed(() => {
  return userStore.user?.bio?.trim() || '这个用户还没有填写个人简介。'
})

function closeMenu() {
  const element = document.activeElement
  if (element && element instanceof HTMLElement) element.blur()
}

async function handleLogout() {
  await userStore.logout()
  closeMenu()
  router.push('/')
}
</script>

<template>
  <div class="dropdown dropdown-end">
    <label tabindex="0" class="cursor-pointer">
      <div class="flex h-10 w-10 items-center justify-center overflow-hidden rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
        <img
          v-if="userStore.user?.photo"
          :src="userStore.user.photo"
          alt="avatar"
          class="h-full w-full object-cover"
        />
        <span v-else>{{ avatarText }}</span>
      </div>
    </label>
    <div
      tabindex="0"
      class="dropdown-content z-[60] mt-3 w-72 overflow-hidden rounded-[28px] border border-gray-100 bg-white shadow-xl"
    >
      <div class="border-b border-gray-100 px-5 py-4">
        <div class="flex items-center gap-3">
          <div class="flex h-12 w-12 items-center justify-center overflow-hidden rounded-full bg-indigo-100 text-sm font-semibold text-indigo-700">
            <img
              v-if="userStore.user?.photo"
              :src="userStore.user.photo"
              alt="avatar"
              class="h-full w-full object-cover"
            />
            <span v-else>{{ avatarText }}</span>
          </div>
          <div class="min-w-0">
            <p class="truncate text-sm font-semibold text-gray-900">{{ userStore.user?.username }}</p>
            <p class="mt-1 line-clamp-2 text-xs leading-5 text-gray-400">{{ bioText }}</p>
          </div>
        </div>
      </div>

      <div class="p-3">
        <RouterLink
          to="/profile/"
          class="flex items-center justify-between rounded-2xl px-4 py-3 text-sm text-gray-600 hover:bg-gray-50"
          @click="closeMenu"
        >
          <span>编辑资料</span>
          <span>›</span>
        </RouterLink>
        <RouterLink
          :to="`/user/${userStore.user?.id || ''}/`"
          class="mt-1 flex items-center justify-between rounded-2xl px-4 py-3 text-sm text-gray-600 hover:bg-gray-50"
          @click="closeMenu"
        >
          <span>我的空间</span>
          <span>›</span>
        </RouterLink>
        <button
          type="button"
          class="mt-1 flex w-full items-center justify-between rounded-2xl px-4 py-3 text-sm text-red-500 hover:bg-red-50"
          @click="handleLogout"
        >
          <span>退出登录</span>
          <span>›</span>
        </button>
      </div>
    </div>
  </div>
</template>
