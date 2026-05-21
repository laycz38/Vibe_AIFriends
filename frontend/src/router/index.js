import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user.js'
import HomepageIndex from '../views/homepage/HomepageIndex.vue'
import FriendIndex from '../views/friend/FriendIndex.vue'
import CreateIndex from '../views/create/CreateIndex.vue'
import NotFoundIndex from '../views/error/NotFoundIndex.vue'
import NoteDetailIndex from '../views/note/NoteDetailIndex.vue'
import LoginIndex from '../views/user/account/LoginIndex.vue'
import RegisterIndex from '../views/user/account/RegisterIndex.vue'
import SpaceIndex from '../views/user/space/SpaceIndex.vue'
import ProfileIndex from '../views/profile/ProfileIndex.vue'
import FavoriteIndex from '../views/favorite/FavoriteIndex.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomepageIndex,
    },
    {
      path: '/friend/',
      name: 'friend',
      component: FriendIndex,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/create/',
      name: 'create',
      component: CreateIndex,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/notes/:note_id/',
      name: 'note-detail',
      component: NoteDetailIndex,
      props: true,
    },
    {
      path: '/user/account/login/',
      name: 'login',
      component: LoginIndex,
    },
    {
      path: '/user/account/register/',
      name: 'register',
      component: RegisterIndex,
    },
    {
      path: '/user/:user_id/',
      name: 'space',
      component: SpaceIndex,
      props: true,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/profile/',
      name: 'profile',
      component: ProfileIndex,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/favorites/',
      name: 'favorites',
      component: FavoriteIndex,
      meta: {
        requiresAuth: true,
      },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: NotFoundIndex,
    },
  ],
})

router.beforeEach((to) => {
  const userStore = useUserStore()

  if (to.meta.requiresAuth && userStore.hasPulledUserInfo && !userStore.isLoggedIn) {
    return {
      name: 'login',
      query: {
        redirect: to.fullPath,
      },
    }
  }

  return true
})

export default router
