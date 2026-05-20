<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <section class="p-6">
    <div class="max-w-2xl mx-auto bg-white rounded-3xl border border-gray-100 p-10 shadow-sm text-center">
      <p class="text-sm text-red-500 font-medium mb-2">404</p>
      <h1 class="text-3xl font-bold text-gray-900 mb-4">页面不存在</h1>
      <p class="text-gray-600 mb-6">你访问的路径没有匹配到前端路由，请检查地址是否正确。</p>
      <RouterLink
        to="/"
        class="inline-flex items-center justify-center rounded-2xl bg-indigo-600 px-5 py-3 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
      >
        返回首页
      </RouterLink>
    </div>
  </section>
</template>
