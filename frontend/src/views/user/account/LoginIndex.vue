<script setup>
import { reactive, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../../stores/user.js'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = reactive({
  username: '',
  password: '',
})

const loading = ref(false)
const errorMessage = ref('')

async function submitLogin() {
  loading.value = true
  errorMessage.value = ''

  try {
    await userStore.login(form)
    router.push(String(route.query.redirect || '/'))
  } catch (error) {
    errorMessage.value = error.message
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <section class="p-6">
    <div class="max-w-md mx-auto bg-white rounded-3xl border border-gray-100 p-8 shadow-sm">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">登录</h1>
      <form class="space-y-4" @submit.prevent="submitLogin">
        <input
          v-model="form.username"
          class="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:border-indigo-500"
          placeholder="用户名"
        />
        <input
          v-model="form.password"
          type="password"
          class="w-full rounded-2xl border border-gray-200 px-4 py-3 outline-none focus:border-indigo-500"
          placeholder="密码"
        />
        <p v-if="errorMessage" class="text-sm text-red-500">
          {{ errorMessage }}
        </p>
        <button
          class="w-full rounded-2xl bg-indigo-600 px-4 py-3 text-sm font-medium text-white hover:bg-indigo-700 transition-colors disabled:cursor-not-allowed disabled:opacity-60"
          :disabled="loading"
        >
          {{ loading ? '登录中...' : '登录' }}
        </button>
      </form>
      <p class="mt-5 text-sm text-gray-500">
        还没有账号？
        <RouterLink to="/user/account/register/" class="text-indigo-600 hover:text-indigo-700">
          去注册
        </RouterLink>
      </p>
    </div>
  </section>
</template>
