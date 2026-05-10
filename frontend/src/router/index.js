import { createRouter, createWebHistory } from 'vue-router'
import { store } from '@/store'
import api from '@/api'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { public: true } },
  { path: '/register', component: () => import('@/views/RegisterView.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('@/layout/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      { path: 'dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'comments', component: () => import('@/views/CommentListView.vue') },
      { path: 'analytics/ip', component: () => import('@/views/Part1View.vue') },
      { path: 'analytics/fans', component: () => import('@/views/Part2View.vue') },
      { path: 'analytics/engagement', component: () => import('@/views/Part3View.vue') },
      { path: 'analytics/sentiment', component: () => import('@/views/Part4View.vue') },
      { path: 'analytics/wordcloud-video', component: () => import('@/views/Part5View.vue') },
      { path: 'analytics/wordcloud-comment', component: () => import('@/views/Part6View.vue') },
      { path: 'predict', component: () => import('@/views/PredictView.vue') },
      { path: 'ai-analyze', component: () => import('@/views/AIAnalyzeView.vue') },
      { path: 'change-password', component: () => import('@/views/ChangePasswordView.vue') },
      { path: 'data-manage', component: () => import('@/views/DataManageView.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  if (to.meta.public) return true

  if (store.user) return true

  // 页面刷新后 store 为空，尝试从 session 恢复
  try {
    const res = await api.get('/auth/me/')
    store.setUser(res.data)
    return true
  } catch {
    return '/login'
  }
})

export default router
