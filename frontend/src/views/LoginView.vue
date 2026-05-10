<template>
  <div class="login-page">
    <!-- Left panel -->
    <div class="left-panel">
      <div class="brand">
        <div class="brand-icon"><el-icon size="28" color="#fff"><VideoCamera /></el-icon></div>
        <h1>短视频分析平台</h1>
        <p>数据驱动内容决策，洞察每一个趋势</p>
      </div>
      <ul class="feature-list">
        <li><el-icon><DataLine /></el-icon>多维数据可视化</li>
        <li><el-icon><TrendCharts /></el-icon>互动数据深度分析</li>
        <li><el-icon><MagicStick /></el-icon>AI 智能内容优化建议</li>
        <li><el-icon><DataAnalysis /></el-icon>点赞数量智能预测</li>
      </ul>
    </div>

    <!-- Right panel -->
    <div class="right-panel">
      <div class="login-box">
        <div class="login-box-header">
          <h2>欢迎回来</h2>
          <p>登录您的账号以继续</p>
        </div>

        <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
          <el-form-item label="用户名" prop="username">
            <el-input
              v-model="form.username"
              placeholder="请输入用户名"
              size="large"
              clearable
              :prefix-icon="User"
            />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              size="large"
              show-password
              :prefix-icon="Lock"
              @keyup.enter="submit"
            />
          </el-form-item>
          <el-form-item style="margin-top:8px">
            <el-button
              type="primary"
              size="large"
              style="width:100%;font-size:15px;height:44px"
              :loading="loading"
              @click="submit"
            >
              登 录
            </el-button>
          </el-form-item>
        </el-form>

        <div class="login-footer">
          还没有账号？
          <el-link type="primary" @click="$router.push('/register')" :underline="false">
            立即注册 →
          </el-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import api from '@/api'
import { store } from '@/store'

const router  = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form  = reactive({ username: '', password: '' })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码',   trigger: 'blur' }],
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await api.post('/auth/login/', form)
    store.setUser(res.data)
    router.push('/dashboard')
    ElMessage.success('登录成功')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
}

/* ── Left branding panel ── */
.left-panel {
  width: 420px;
  flex-shrink: 0;
  background: linear-gradient(160deg, #0f172a 0%, #1e3a5f 60%, #1a4780 100%);
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px 48px;
  position: relative;
  overflow: hidden;
}
.left-panel::before {
  content: '';
  position: absolute;
  top: -80px; right: -80px;
  width: 320px; height: 320px;
  border-radius: 50%;
  background: rgba(64,158,255,0.08);
}
.left-panel::after {
  content: '';
  position: absolute;
  bottom: -60px; left: -60px;
  width: 240px; height: 240px;
  border-radius: 50%;
  background: rgba(64,158,255,0.06);
}

.brand {
  margin-bottom: 48px;
  position: relative;
  z-index: 1;
}
.brand-icon {
  width: 56px; height: 56px;
  border-radius: 14px;
  background: linear-gradient(135deg, #409EFF, #337ecc);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 20px;
  box-shadow: 0 8px 24px rgba(64,158,255,0.35);
}
.brand h1 {
  margin: 0 0 10px;
  font-size: 24px;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.02em;
}
.brand p {
  margin: 0;
  font-size: 14px;
  color: rgba(255,255,255,0.45);
  line-height: 1.6;
}

.feature-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 16px;
  position: relative;
  z-index: 1;
}
.feature-list li {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: rgba(255,255,255,0.6);
}
.feature-list li .el-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  background: rgba(64,158,255,0.15);
  color: #60a5fa;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 15px;
}

/* ── Right form panel ── */
.right-panel {
  flex: 1;
  background: #f8fafc;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

.login-box {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08), 0 0 0 1px rgba(0,0,0,0.04);
}

.login-box-header {
  margin-bottom: 28px;
}
.login-box-header h2 {
  margin: 0 0 6px;
  font-size: 22px;
  font-weight: 700;
  color: #0f172a;
}
.login-box-header p {
  margin: 0;
  font-size: 14px;
  color: #94a3b8;
}

.login-footer {
  text-align: center;
  margin-top: 20px;
  font-size: 13px;
  color: #94a3b8;
}
</style>
