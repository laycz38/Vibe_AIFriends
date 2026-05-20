<script setup>
defineProps({
  user_id: {
    type: String,
    required: true,
  },
})
</script>

<template>
  <section class="p-6">
    <div class="max-w-3xl mx-auto bg-white rounded-3xl border border-gray-100 p-8 shadow-sm">
      <p class="text-sm text-indigo-500 font-medium mb-2">User Space</p>
      <h1 class="text-3xl font-bold text-gray-900 mb-4">个人空间</h1>
      <p class="text-gray-600 mb-2">当前路由传入的 user_id 为：</p>
      <div class="inline-flex items-center rounded-2xl bg-indigo-50 px-4 py-2 text-indigo-700 font-medium">
        {{ user_id }}
      </div>
    </div>
  </section>
</template>
