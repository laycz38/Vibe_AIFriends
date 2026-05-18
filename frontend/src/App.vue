<script setup>
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import FeedWaterfall from './components/FeedWaterfall.vue'
</script>

<template>
  <div class="min-h-screen bg-[#f7f7f7]">
    <Sidebar />
    <Header />
    <main class="pl-[280px] pt-[120px]">
      <FeedWaterfall />
    </main>
  </div>
</template>
