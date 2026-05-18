<script setup>
import { ref } from 'vue'
import { categories } from '../data/notes.js'

const activeTab = ref('推荐')

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
            placeholder="登录探索更多内容"
            class="w-full h-10 bg-gray-100 rounded-full pl-5 pr-12 text-sm text-gray-700 placeholder-gray-400 outline-none focus:bg-white focus:ring-2 focus:ring-[#ff2442]/20 transition-all"
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
        <a href="#" class="text-sm text-gray-500 hover:text-gray-700 transition-colors">
          创作中心
        </a>
        <a href="#" class="text-sm text-gray-500 hover:text-gray-700 transition-colors">
          业务合作
        </a>
      </div>
    </div>

    <div class="flex items-center gap-6 px-6 mt-[2px] overflow-x-auto scrollbar-hide">
      <button
        v-for="tab in categories"
        :key="tab"
        @click="selectTab(tab)"
        class="whitespace-nowrap text-sm pb-1 transition-colors border-b-2 flex-shrink-0"
        :class="activeTab === tab
          ? 'text-gray-900 font-semibold border-[#ff2442]'
          : 'text-gray-500 border-transparent hover:text-gray-700'"
      >
        {{ tab }}
      </button>
    </div>
  </header>
</template>
