import axios from 'axios'
import { useUserStore } from '@/stores/user.js'

const BASE_URL = import.meta.env.DEV ? 'http://127.0.0.1:8000' : ''

const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true,
  timeout: 5000,
})

api.interceptors.request.use((config) => {
  const userStore = useUserStore()
  if (userStore.accessToken) {
    config.headers.Authorization = `Bearer ${userStore.accessToken}`
  }
  return config
})

let isRefreshing = false
let refreshSubscribers = []

function subscribeTokenRefresh(callback) {
  refreshSubscribers.push(callback)
}

function onRefreshed(token) {
  refreshSubscribers.forEach((callback) => callback(token))
  refreshSubscribers = []
}

function onRefreshFailed(error) {
  refreshSubscribers.forEach((callback) => callback(null, error))
  refreshSubscribers = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const userStore = useUserStore()
    const originalRequest = error?.config

    if (!originalRequest) {
      return Promise.reject(error)
    }

    const isRefreshRequest = String(originalRequest.url || '').includes('/api/user/account/refresh_token/')
    if (isRefreshRequest) {
      userStore.clearAuth()
      userStore.hasPulledUserInfo = true
      return Promise.reject(error)
    }

    if (error.response?.status === 401 && !originalRequest._retry) {
      // 登录、注册等公开接口不需要刷新 token
      const url = String(originalRequest.url || '')
      const isAuthEndpoint = url.includes('/api/user/account/login/') ||
                             url.includes('/api/user/account/register/')
      if (isAuthEndpoint) {
        return Promise.reject(error)
      }

      originalRequest._retry = true

      return new Promise((resolve, reject) => {
        subscribeTokenRefresh((token, refreshError) => {
          if (refreshError || !token) {
            reject(error)
            return
          }

          originalRequest.headers.Authorization = `Bearer ${token}`
          resolve(api(originalRequest))
        })

        if (!isRefreshing) {
          isRefreshing = true
          axios.post(
            `${BASE_URL}/api/user/account/refresh_token/`,
            {},
            { withCredentials: true, timeout: 5000 },
          ).then((response) => {
            const newToken = response.data.access || response.data.access_token
            if (!newToken) {
              throw new Error('刷新 access token 失败')
            }
            userStore.setAccessToken(newToken)
            onRefreshed(newToken)
          }).catch((refreshError) => {
            userStore.clearAuth()
            userStore.hasPulledUserInfo = true
            onRefreshFailed(refreshError)
          }).finally(() => {
            isRefreshing = false
          })
        }
      })
    }

    return Promise.reject(error)
  },
)

export default api
