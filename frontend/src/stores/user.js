import { defineStore } from 'pinia'
import api from '@/js/http/api.js'

function loadStoredUser() {
  const rawUser = localStorage.getItem('user_info')
  if (!rawUser) return null

  try {
    return JSON.parse(rawUser)
  } catch {
    localStorage.removeItem('user_info')
    return null
  }
}

export const useUserStore = defineStore('user', {
  state: () => ({
    accessToken: localStorage.getItem('access_token') || '',
    user: loadStoredUser(),
    hasPulledUserInfo: false,
  }),
  getters: {
    isLoggedIn: (state) => Boolean(state.accessToken && state.user),
  },
  actions: {
    setAccessToken(accessToken) {
      this.accessToken = accessToken || ''
      if (this.accessToken) {
        localStorage.setItem('access_token', this.accessToken)
      } else {
        localStorage.removeItem('access_token')
      }
    },
    setUser(user) {
      this.user = user
      if (user) {
        localStorage.setItem('user_info', JSON.stringify(user))
      } else {
        localStorage.removeItem('user_info')
      }
    },
    setAuth(accessToken, user) {
      this.setAccessToken(accessToken)
      this.setUser(user)
      this.hasPulledUserInfo = true
    },
    clearAuth() {
      this.setAccessToken('')
      this.setUser(null)
    },
    async handleAuthResponse(response) {
      const data = response.data || {}
      const accessToken = data.access || data.access_token
      if (!accessToken || data.result !== 'success') {
        throw new Error(data.message || '请求失败')
      }

      this.setAuth(accessToken, data.user)
      return data
    },
    async login(payload) {
      const response = await api.post('/api/user/account/login/', payload)
      return this.handleAuthResponse(response)
    },
    async register(payload) {
      const response = await api.post('/api/user/account/register/', payload)
      return this.handleAuthResponse(response)
    },
    async pullUserInfo() {
      if (this.hasPulledUserInfo) {
        return this.user
      }

      try {
        const response = await api.get('/api/user/account/info/')
        this.setUser(response.data.user)
        return this.user
      } catch (error) {
        this.clearAuth()
        return null
      } finally {
        this.hasPulledUserInfo = true
      }
    },
    async updateProfile(payload) {
      const response = await api.post('/api/user/account/update_profile/', payload)
      if (response.data?.result !== 'success') {
        throw new Error(response.data?.message || '更新资料失败')
      }
      this.setUser(response.data.user)
      this.hasPulledUserInfo = true
      return response.data.user
    },
    async refreshToken() {
      try {
        const response = await api.post('/api/user/account/refresh_token/', {})
        const accessToken = response.data.access || response.data.access_token
        if (accessToken) {
          this.setAccessToken(accessToken)
        }
        if (response.data?.user) {
          this.setUser(response.data.user)
        }
        return response.data
      } catch (error) {
        this.clearAuth()
        this.hasPulledUserInfo = true
        return null
      }
    },
    async logout() {
      try {
        await api.post('/api/user/account/logout/', {})
      } finally {
        this.clearAuth()
        this.hasPulledUserInfo = true
      }
    },
  },
})
