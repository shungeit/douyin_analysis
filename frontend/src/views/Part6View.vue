<template>
  <el-card v-loading="loading">
    <template #header>
      <div class="card-title"><el-icon style="color:#5470c6"><Comment /></el-icon>评论词云图</div>
    </template>
    <div v-if="url" class="img-wrap">
      <el-image :src="url" fit="contain" style="max-width:100%;max-height:580px;border-radius:8px" />
    </div>
    <div v-else class="empty-hint">
      <el-icon size="48" color="#e2e8f0"><Comment /></el-icon>
      <p>词云图暂未生成，请在「数据管理」中点击「生成词云」</p>
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'

const loading = ref(false)
const url     = ref('')

onMounted(async () => {
  loading.value = true
  try {
    const res  = await api.get('/charts/wordcloud/comment/')
    const base = res.data.url?.split('?')[0]
    url.value  = base ? `${base}?t=${Date.now()}` : ''
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.card-title { display: flex; align-items: center; gap: 7px; }
.img-wrap   { display: flex; justify-content: center; padding: 12px 0; }
.empty-hint {
  display: flex; flex-direction: column; align-items: center;
  padding: 80px 0; gap: 14px; color: #cbd5e1;
}
.empty-hint p { margin: 0; font-size: 14px; }
</style>
