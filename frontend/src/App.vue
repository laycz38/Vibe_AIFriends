<script setup>
import { onMounted, ref } from 'vue'
import { RouterView } from 'vue-router'
import router from './router'
import Sidebar from './components/Sidebar.vue'
import Header from './components/Header.vue'
import { useUserStore } from './stores/user.js'

const userStore = useUserStore()
const isSidebarExpanded = ref(false)

function toggleSidebar() {
  isSidebarExpanded.value = !isSidebarExpanded.value
}

onMounted(async () => {
  await userStore.pullUserInfo()

  const currentRoute = router.currentRoute.value
  if (currentRoute.meta.requiresAuth && !userStore.isLoggedIn) {
    router.replace({
      name: 'login',
      query: {
        redirect: currentRoute.fullPath,
      },
    })
  }
})
</script>

<template>
  <div class="min-h-screen bg-[#f7f7f7]">
    <Sidebar :expanded="isSidebarExpanded" />
    <Header :sidebar-expanded="isSidebarExpanded" @toggle-sidebar="toggleSidebar" />
    <main
      class="pt-[120px] transition-all duration-300"
      :class="isSidebarExpanded ? 'pl-[220px]' : 'pl-[72px]'"
    >
      <RouterView />
    </main>
  </div>
</template>
