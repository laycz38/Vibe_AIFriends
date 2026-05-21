<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MenuIcon from './icons/MenuIcon.vue'
import HomepageIcon from './icons/HomepageIcon.vue'
import FriendIcon from './icons/FriendIcon.vue'
import CreateIcon from './icons/CreateIcon.vue'
import StarIcon from './icons/StarIcon.vue'
import SearchIcon from './icons/SearchIcon.vue'
import { useUserStore } from '@/stores/user.js'
import UserMenu from './UserMenu.vue'

const user = useUserStore()
const router = useRouter()
const route = useRoute()
const searchQuery = ref('')

watch(() => route.query.q, (newQ) => {
  searchQuery.value = newQ || ''
})

function handleSearch() {
  router.push({
    name: 'home',
    query: {
      q: searchQuery.value.trim(),
    },
  })
}
</script>

<template>
  <div class="drawer lg:drawer-open">
    <input id="my-drawer" type="checkbox" class="drawer-toggle" />
    <div class="drawer-content">
      <nav class="navbar w-full bg-base-100 shadow-sm">
        <div class="navbar-start">
          <label for="my-drawer" aria-label="open sidebar" class="btn btn-square btn-ghost lg:hidden">
            <MenuIcon />
          </label>
          <div class="px-2 font-bold text-xl">AI 面经</div>
        </div>
        <div class="navbar-center hidden sm:flex sm:w-4/5 sm:max-w-180 sm:justify-center">
          <form @submit.prevent="handleSearch" class="join w-4/5 flex justify-center">
            <input v-model="searchQuery" class="input join-item rounded-l-full w-4/5" placeholder="搜索面经、公司、岗位..." />
            <button class="btn join-item rounded-r-full gap-0">
              <SearchIcon />
              搜索
            </button>
          </form>
        </div>
        <div class="navbar-end">
          <template v-if="user.hasPulledUserInfo">
            <RouterLink
              v-if="user.isLoggedIn"
              :to="{ name: 'create' }"
              active-class="btn-active"
              class="btn btn-ghost text-base mr-6"
            >
              <CreateIcon />
              创作
            </RouterLink>
            <UserMenu v-if="user.isLoggedIn" />
            <RouterLink
              v-else
              :to="{ name: 'login' }"
              class="btn btn-ghost text-lg"
            >
              登录
            </RouterLink>
          </template>
        </div>
      </nav>
      <slot></slot>
    </div>

    <div class="drawer-side z-50 is-drawer-close:overflow-visible">
      <label for="my-drawer" aria-label="close sidebar" class="drawer-overlay"></label>
      <div class="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-16 is-drawer-open:w-54">
        <ul class="menu w-full grow pt-4">
          <li>
            <RouterLink
              :to="{ name: 'home' }"
              active-class="menu-active"
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3"
              data-tip="首页"
            >
              <HomepageIcon />
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">首页</span>
            </RouterLink>
          </li>
          <li>
            <RouterLink
              :to="{ name: 'friend' }"
              active-class="menu-active"
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3"
              data-tip="AI 问答"
            >
              <FriendIcon />
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">AI 问答</span>
            </RouterLink>
          </li>
          <li>
            <RouterLink
              :to="{ name: 'create' }"
              active-class="menu-active"
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3"
              data-tip="发布面经"
            >
              <CreateIcon />
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">发布面经</span>
            </RouterLink>
          </li>
          <li>
            <RouterLink
              :to="{ name: 'profile' }"
              active-class="menu-active"
              class="is-drawer-close:tooltip is-drawer-close:tooltip-right py-3"
              data-tip="我的收藏"
            >
              <StarIcon />
              <span class="is-drawer-close:hidden text-base ml-2 whitespace-nowrap">我的收藏</span>
            </RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>
