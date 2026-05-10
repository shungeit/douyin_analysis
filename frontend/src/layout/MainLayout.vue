<template>
  <div class="layout-root">
    <!-- ── Sidebar ── -->
    <aside class="sidebar" :class="{ collapsed }">
      <!-- Logo -->
      <div class="sidebar-logo">
        <div class="logo-mark">
          <el-icon size="15" color="#fff"><VideoCamera /></el-icon>
        </div>
        <span v-if="!collapsed" class="logo-text">短视频分析平台</span>
      </div>

      <!-- Navigation -->
      <nav class="sidebar-nav">
        <template v-for="section in sections" :key="section.label">
          <div v-if="!collapsed" class="nav-group-label">{{ section.label }}</div>
          <div v-else class="nav-group-divider"></div>
          <el-tooltip
            v-for="item in section.items"
            :key="item.to"
            :content="item.label"
            placement="right"
            :disabled="!collapsed"
            :show-after="300"
          >
            <router-link :to="item.to" class="nav-item" :class="{ active: route.path === item.to }">
              <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
              <span v-if="!collapsed" class="nav-label">{{ item.label }}</span>
            </router-link>
          </el-tooltip>
        </template>
      </nav>

      <!-- Collapse button -->
      <button class="collapse-btn" @click="collapsed = !collapsed">
        <el-icon size="13"><component :is="collapsed ? 'Expand' : 'Fold'" /></el-icon>
        <span v-if="!collapsed">收起侧栏</span>
      </button>
    </aside>

    <!-- ── Main ── -->
    <div class="main-wrapper">
      <!-- Header -->
      <header class="site-header">
        <h1 class="page-title">{{ currentTitle }}</h1>
        <div class="header-right">
          <el-dropdown trigger="click">
            <div class="user-chip">
              <div class="user-avatar">{{ store.user?.username?.[0]?.toUpperCase() || 'U' }}</div>
              <span class="user-name">{{ store.user?.username }}</span>
              <el-icon size="11" style="color:#94a3b8;margin-left:2px"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="$router.push('/change-password')">
                  <el-icon><Lock /></el-icon>修改密码
                </el-dropdown-item>
                <el-dropdown-item divided @click="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- Page content -->
      <main class="page-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { store } from '@/store'

const route  = useRoute()
const router = useRouter()
const collapsed = ref(false)

const sections = [
  {
    label: '概览',
    items: [
      { to: '/dashboard', icon: 'DataLine',     label: '仪表盘'   },
      { to: '/comments',  icon: 'ChatDotRound', label: '评论管理' },
    ],
  },
  {
    label: '数据分析',
    items: [
      { to: '/analytics/ip',               icon: 'MapLocation',  label: '地区分布' },
      { to: '/analytics/fans',             icon: 'UserFilled',   label: '粉丝分析' },
      { to: '/analytics/engagement',       icon: 'TrendCharts',  label: '互动分析' },
      { to: '/analytics/sentiment',        icon: 'Sunny',        label: '情感分析' },
      { to: '/analytics/wordcloud-video',  icon: 'Film',         label: '视频词云' },
      { to: '/analytics/wordcloud-comment',icon: 'Comment',      label: '评论词云' },
    ],
  },
  {
    label: '智能功能',
    items: [
      { to: '/predict',    icon: 'DataAnalysis', label: '点赞预测'    },
      { to: '/ai-analyze', icon: 'MagicStick',   label: 'AI 智能分析' },
    ],
  },
  {
    label: '系统',
    items: [
      { to: '/data-manage', icon: 'Setting', label: '数据管理' },
    ],
  },
]

const titleMap = {
  '/dashboard':                   '仪表盘',
  '/comments':                    '评论管理',
  '/analytics/ip':                '地区分布',
  '/analytics/fans':              '粉丝分析',
  '/analytics/engagement':        '互动分析',
  '/analytics/sentiment':         '情感分析',
  '/analytics/wordcloud-video':   '视频词云',
  '/analytics/wordcloud-comment': '评论词云',
  '/predict':                     '点赞预测',
  '/ai-analyze':                  'AI 智能分析',
  '/data-manage':                 '数据管理',
  '/change-password':             '修改密码',
}

const currentTitle = computed(() => titleMap[route.path] || '短视频分析平台')

async function logout() {
  await api.post('/auth/logout/')
  store.clearUser()
  router.push('/login')
  ElMessage.success('已退出登录')
}
</script>

<style scoped>
/* ── Root layout ── */
.layout-root {
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* ── Sidebar ── */
.sidebar {
  width: 220px;
  min-width: 220px;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  transition: width 0.22s ease, min-width 0.22s ease;
  overflow: hidden;
}
.sidebar.collapsed {
  width: 64px;
  min-width: 64px;
}

/* Logo */
.sidebar-logo {
  height: 58px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  flex-shrink: 0;
  overflow: hidden;
  white-space: nowrap;
}
.logo-mark {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.logo-text {
  font-size: 14px;
  font-weight: 600;
  color: #f1f5f9;
  letter-spacing: 0.01em;
}

/* Nav */
.sidebar-nav {
  flex: 1;
  padding: 8px 8px;
  overflow-y: auto;
  overflow-x: hidden;
}
.sidebar-nav::-webkit-scrollbar { width: 4px; }
.sidebar-nav::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

.nav-group-label {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255,255,255,0.28);
  padding: 14px 8px 5px;
  white-space: nowrap;
}
.nav-group-divider {
  height: 1px;
  background: rgba(255,255,255,0.07);
  margin: 6px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 7px;
  margin-bottom: 1px;
  color: rgba(255,255,255,0.55);
  text-decoration: none;
  font-size: 13.5px;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
  overflow: hidden;
}
.nav-item:hover {
  background: rgba(255,255,255,0.07);
  color: rgba(255,255,255,0.9);
}
.nav-item.active {
  background: rgba(64,158,255,0.18);
  color: #60a5fa;
}
.nav-item.active .nav-icon {
  color: #409EFF;
}
.nav-icon {
  flex-shrink: 0;
  font-size: 15px;
}
.nav-label {
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Collapse button */
.collapse-btn {
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: rgba(255,255,255,0.35);
  font-size: 12px;
  background: none;
  border: none;
  border-top: 1px solid rgba(255,255,255,0.07);
  cursor: pointer;
  flex-shrink: 0;
  transition: color 0.15s, background 0.15s;
  width: 100%;
}
.collapse-btn:hover {
  color: rgba(255,255,255,0.75);
  background: rgba(255,255,255,0.05);
}

/* ── Main wrapper ── */
.main-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
.site-header {
  height: 58px;
  background: #fff;
  border-bottom: 1px solid #e8edf2;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.page-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  letter-spacing: -0.01em;
}

/* User chip */
.user-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px 5px 5px;
  border-radius: 20px;
  border: 1px solid #e8edf2;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.user-chip:hover {
  border-color: #409EFF;
  box-shadow: 0 0 0 3px rgba(64,158,255,0.1);
}
.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #409EFF 0%, #337ecc 100%);
  color: #fff;
  font-size: 12px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}
.user-name {
  font-size: 13px;
  font-weight: 500;
  color: #334155;
}

/* Page content */
.page-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px 24px;
  background: var(--bg);
}
</style>
