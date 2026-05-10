<template>
  <div class="page-center">
    <el-card class="pwd-card">
      <template #header>
        <div class="card-title-row">
          <el-icon style="color:#409EFF;font-size:16px"><Lock /></el-icon>
          <span>修改密码</span>
        </div>
      </template>

      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="原始密码" prop="old_password">
          <el-input v-model="form.old_password" type="password" show-password placeholder="请输入当前密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="form.new_password" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认新密码" prop="confirm_password">
          <el-input v-model="form.confirm_password" type="password" show-password placeholder="再次输入新密码" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="loading" @click="submit">确认修改</el-button>
          <el-button @click="formRef.resetFields()">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const formRef = ref(null)
const loading = ref(false)
const form    = reactive({ old_password: '', new_password: '', confirm_password: '' })

const rules = {
  old_password:     [{ required: true, message: '请输入原始密码', trigger: 'blur' }],
  new_password:     [{ required: true, message: '请输入新密码',   trigger: 'blur' }],
  confirm_password: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { validator: (_, v, cb) => v !== form.new_password ? cb(new Error('两次密码不一致')) : cb(), trigger: 'blur' },
  ],
}

async function submit() {
  await formRef.value.validate()
  loading.value = true
  try {
    await api.post('/auth/change-password/', form)
    ElMessage.success('密码修改成功')
    formRef.value.resetFields()
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '修改失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page-center {
  display: flex;
  justify-content: center;
  padding-top: 20px;
}
.pwd-card {
  width: 100%;
  max-width: 500px;
}
.card-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
