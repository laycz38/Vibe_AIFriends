<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { categories } from '../data/notes.js'
import { useUserStore } from '../stores/user.js'
import UserMenu from './navbar/UserMenu.vue'

const activeTab = ref('全部')
const userStore = useUserStore()

function selectTab(tab) {
  activeTab.value = tab
}
</script>

<template>
  <header
    class="fixed top-0 left-[280px] right-0 h-[72px] bg-white border-b border-gray-100 z-40 flex flex-col justify-center"
  >
    <div class="flex items-center justify-between px-6">
      <div class="flex-1 flex justify-center">
        <div class="relative w-full max-w-[600px]">
          <input
            type="text"
            placeholder="搜索面经、公司、岗位..."
            class="w-full h-10 bg-gray-100 rounded-full pl-5 pr-12 text-sm text-gray-700 placeholder-gray-400 outline-none focus:bg-white focus:ring-2 focus:ring-indigo-500/20 transition-all"
          />
          <svg
            class="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="M21 21l-4.35-4.35" />
          </svg>
        </div>
      </div>

      <div class="flex items-center gap-4 ml-6">
        <RouterLink
          to="/friend/"
          class="text-sm text-gray-500 hover:text-indigo-600 transition-colors"
          active-class="text-indigo-600 font-medium"
        >
          AI 模拟面试
        </RouterLink>
        <template v-if="userStore.hasPulledUserInfo">
          <RouterLink
            v-if="userStore.isLoggedIn"
            to="/create/"
            class="inline-flex items-center rounded-full bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
            active-class="bg-indigo-700"
          >
            创作
          </RouterLink>
          <UserMenu v-if="userStore.isLoggedIn" />
          <RouterLink
            v-else
            to="/user/account/login/"
            class="text-sm text-gray-500 hover:text-indigo-600 transition-colors"
            active-class="text-indigo-600 font-medium"
          >
            登录
          </RouterLink>
          <RouterLink
            v-if="!userStore.isLoggedIn"
            to="/user/account/register/"
            class="text-sm text-gray-500 hover:text-indigo-600 transition-colors"
            active-class="text-indigo-600 font-medium"
          >
            注册
          </RouterLink>
        </template>
        <div v-else class="h-10 w-24 rounded-full bg-gray-100 animate-pulse"></div>
      </div>
    </div>

    <div class="flex items-center gap-6 px-6 mt-[2px] overflow-x-auto scrollbar-hide">
      <button
        v-for="tab in categories"
        :key="tab"
        @click="selectTab(tab)"
        class="whitespace-nowrap text-sm pb-1 transition-colors border-b-2 flex-shrink-0"
        :class="activeTab === tab
          ? 'text-gray-900 font-semibold border-indigo-500'
          : 'text-gray-500 border-transparent hover:text-gray-700'"
      >
        {{ tab }}
      </button>
    </div>
  </header>
</template>
