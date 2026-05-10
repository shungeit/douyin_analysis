import axios from 'axios'
import router from '@/router'
import { store } from '@/store'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,  // 默认 30s
})

// NLP / 词云 等耗时操作使用更长超时
export function apiLong() {
  return axios.create({
    baseURL: '/api',
    withCredentials: true,
    headers: { 'Content-Type': 'application/json' },
    timeout: 180000,  // 3 分钟
  })
}

// 所有 GET 请求加时间戳，防止浏览器缓存旧响应
api.interceptors.request.use(config => {
  if (config.method === 'get') {
    config.params = { ...config.params, _t: Date.now() }
  }
  return config
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401 || err.response?.status === 403) {
      store.clearUser()
      router.push('/login')
    }
    return Promise.reject(err)
  }
)

export default api
