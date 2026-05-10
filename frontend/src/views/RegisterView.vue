<template>
  <div class="register-page">
    <div class="register-box">
      <div class="box-header">
        <div class="logo-mark"><el-icon size="18" color="#fff"><VideoCamera /></el-icon></div>
        <h2>创建账号</h2>
        <p>注册后即可使用全部功能</p>
      </div>

      <el-form :model="form" :rules="rules" ref="formRef" label-position="top">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" size="large" clearable :prefix-icon="User" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" size="large" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirm">
          <el-input v-model="form.confirm" type="password" placeholder="再次输入密码" size="large" show-password :prefix-icon="Lock" @keyup.enter="submit" />
        </el-form-item>
        <el-form-item style="margin-top:8px">
          <el-button type="primary" size="large" style="width:100%;height:44px;font-size:15px" :loading="loading" @click="submit">
            注 册
          </el-button>
        </el-form-item>
      </el-form>

      <div class="footer">
        已有账号？
        <el-link type="primary" @click="$router.push('/login')" :underline="false">立即登录 →</el-link>
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

const router  = useRouter()
const formRef = ref(null)
const loading = ref(false)
const form    = reactive({ username: '', password: '', confirm: '' })
const rules   = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码',   trigger: 'blur' }],
  confirm:  [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: (_, v, cb) => v !== form.password ? cb(new Error('两次密码不一致')) : cb(), trigger: 'blur' },
  ],
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await api.post('/auth/register/', { username: form.username, password: form.password })
    ElMessage.success('注册成功，请登录')
    router.push('/login')
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '注册失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-page {
  min-height: 100vh;
  background: linear-gradient(160deg, #0f172a 0%, #1e3a5f 60%, #f0f2f5 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
}
.register-box {
  width: 100%;
  max-width: 420px;
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
}
.box-header { text-align: center; margin-bottom: 28px; }
.logo-mark {
  width: 48px; height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #409EFF, #337ecc);
  display: flex; align-items: center; justify-content: center;
  margin: 0 auto 16px;
  box-shadow: 0 6px 16px rgba(64,158,255,0.3);
}
.box-header h2 { margin: 0 0 6px; font-size: 22px; font-weight: 700; color: #0f172a; }
.box-header p  { margin: 0; font-size: 14px; color: #94a3b8; }
.footer { text-align: center; margin-top: 20px; font-size: 13px; color: #94a3b8; }
</style>
