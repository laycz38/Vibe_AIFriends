<script setup>
import { sidebarMenuItems } from '../data/notes.js'
</script>

<template>
  <aside
    class="fixed top-0 left-0 h-screen w-[280px] bg-white border-r border-gray-100 flex flex-col z-50 overflow-y-auto"
  >
    <div class="px-6 pt-6 pb-4">
      <div class="flex items-center gap-2">
        <div class="w-9 h-9 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl flex items-center justify-center">
          <span class="text-white font-bold text-sm">AI</span>
        </div>
        <span class="text-lg font-bold text-gray-900">AI 面经</span>
      </div>
    </div>

    <nav class="flex-1 px-3">
      <ul class="space-y-1">
        <li
          v-for="item in sidebarMenuItems"
          :key="item.name"
        >
          <a
            href="#"
            class="flex items-center gap-3 px-4 py-3 rounded-xl text-[15px] transition-colors"
            :class="item.active
              ? 'bg-indigo-50 text-indigo-700 font-medium'
              : 'text-gray-600 hover:bg-gray-50'"
          >
            <span class="text-lg">{{ item.icon }}</span>
            <span>{{ item.name }}</span>
          </a>
        </li>
      </ul>
    </nav>

    <div class="px-4 py-3">
      <button
        class="w-full py-2.5 bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white rounded-xl text-sm font-medium transition-all shadow-sm hover:shadow-md"
      >
        立即登录
      </button>
    </div>

    <div class="px-4 pb-3">
      <div class="border border-gray-200 rounded-xl p-3 text-xs text-gray-400 leading-relaxed">
        <p class="font-medium text-gray-500 mb-1 text-[13px]">登录即可体验</p>
        <p class="mb-0.5">· AI 智能检索面经</p>
        <p class="mb-0.5">· 收藏你关注的公司</p>
        <p>· 分享你的面试经验</p>
      </div>
    </div>

    <div class="px-4 pb-6">
      <a
        href="#"
        class="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm text-gray-500 hover:bg-gray-50 transition-colors"
      >
        <span>☰</span>
        <span>更多</span>
      </a>
    </div>
  </aside>
</template>
