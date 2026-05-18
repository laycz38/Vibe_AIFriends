<script setup>
import { sidebarMenuItems } from '../data/notes.js'
</script>

<template>
  <aside
    class="fixed top-0 left-0 h-screen w-[280px] bg-white border-r border-gray-100 flex flex-col z-50 overflow-y-auto"
  >
    <div class="px-6 pt-6 pb-4">
      <div class="flex items-center gap-2">
        <div class="w-9 h-9 bg-[#ff2442] rounded-xl flex items-center justify-center">
          <span class="text-white font-bold text-sm">红</span>
        </div>
        <span class="text-lg font-bold text-gray-900">小红书</span>
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
              ? 'bg-gray-100 text-gray-900 font-medium'
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
        class="w-full py-2.5 bg-[#ff2442] hover:bg-[#e0203c] text-white rounded-xl text-sm font-medium transition-colors"
      >
        登录
      </button>
    </div>

    <div class="px-4 pb-3">
      <div class="border border-gray-200 rounded-xl p-3 text-xs text-gray-400 leading-relaxed">
        <p class="font-medium text-gray-500 mb-1 text-[13px]">马上登录即可</p>
        <p class="mb-0.5">· 点赞收藏你喜欢的笔记</p>
        <p class="mb-0.5">· 关注你感兴趣的博主</p>
        <p>· 发布属于你的创作内容</p>
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
