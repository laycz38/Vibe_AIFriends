<script setup>
import { onMounted } from 'vue'
import { RouterView } from 'vue-router'
import router from './router'
import NavBar from './components/navbar/NavBar.vue'
import { useUserStore } from './stores/user.js'

const userStore = useUserStore()

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
  <NavBar>
    <RouterView />
  </NavBar>
</template>
