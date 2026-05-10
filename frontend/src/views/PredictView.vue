<template>
  <el-row :gutter="20">
    <!-- 输入表单 -->
    <el-col :span="10">
      <el-card>
        <template #header>
          <div class="card-title-row">
            <el-icon style="color:#409EFF;font-size:16px"><DataAnalysis /></el-icon>
            <span>输入视频参数</span>
          </div>
        </template>
        <el-form :model="form" :rules="rules" ref="formRef" label-width="106px" label-position="left">
          <el-form-item prop="duration">
            <template #label><span class="form-label">视频时长<em>秒</em></span></template>
            <el-input-number v-model="form.duration" :min="0" :max="600" style="width:100%" />
          </el-form-item>
          <el-form-item prop="fans">
            <template #label><span class="form-label">粉丝数量</span></template>
            <el-input-number v-model="form.fans" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item prop="collect">
            <template #label><span class="form-label">收藏数量</span></template>
            <el-input-number v-model="form.collect" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item prop="comment">
            <template #label><span class="form-label">评论数量</span></template>
            <el-input-number v-model="form.comment" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item prop="share">
            <template #label><span class="form-label">分享数量</span></template>
            <el-input-number v-model="form.share" :min="0" style="width:100%" />
          </el-form-item>
          <el-form-item prop="interaction_rate">
            <template #label><span class="form-label">互动率<em>小数</em></span></template>
            <el-input-number v-model="form.interaction_rate" :min="0" :step="0.001" :precision="4" style="width:100%" />
          </el-form-item>
          <el-form-item prop="hour">
            <template #label><span class="form-label">发布小时<em>0-23</em></span></template>
            <el-input-number v-model="form.hour" :min="0" :max="23" style="width:100%" />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" :loading="loading" @click="predict" style="width:100%">
              <el-icon><DataAnalysis /></el-icon>&nbsp;开始预测
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </el-col>

    <!-- 结果 -->
    <el-col :span="14">
      <el-card style="min-height:460px">
        <template #header>
          <div class="card-title-row">
            <el-icon style="color:#10b981;font-size:16px"><TrendCharts /></el-icon>
            <span>预测结果</span>
          </div>
        </template>

        <div v-if="result !== null" class="result-wrap">
          <!-- 主数字 -->
          <div class="result-hero">
            <div class="result-hero-label">预测点赞数</div>
            <div class="result-hero-value">{{ Number(result).toLocaleString() }}</div>
            <div class="result-hero-sub">
              <el-icon style="color:#f59e0b"><Promotion /></el-icon>
              基于当前输入参数的模型预测值
            </div>
          </div>

          <el-divider />

          <!-- 参数回显 -->
          <div class="param-grid">
            <div class="param-item" v-for="p in paramList" :key="p.label">
              <span class="param-label">{{ p.label }}</span>
              <span class="param-value">{{ p.value }}</span>
            </div>
          </div>
        </div>

        <div v-else class="empty-hint">
          <el-icon size="52" color="#e2e8f0"><DataAnalysis /></el-icon>
          <p>填写左侧参数后点击「开始预测」</p>
        </div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const formRef = ref(null)
const loading = ref(false)
const result  = ref(null)

const form = reactive({
  duration: 60, fans: 1000, collect: 0, comment: 0,
  share: 0, interaction_rate: 0.05, hour: 20,
})

const rules = Object.fromEntries(
  Object.keys(form).map(k => [k, [{ required: true, message: '必填', trigger: 'blur' }]])
)

const paramList = computed(() => [
  { label: '视频时长(秒)', value: form.duration },
  { label: '粉丝数量',     value: form.fans.toLocaleString() },
  { label: '收藏数量',     value: form.collect.toLocaleString() },
  { label: '评论数量',     value: form.comment.toLocaleString() },
  { label: '分享数量',     value: form.share.toLocaleString() },
  { label: '互动率',       value: form.interaction_rate },
  { label: '发布小时',     value: `${form.hour}:00` },
])

async function predict() {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await api.post('/predict/', form)
    result.value = res.data.prediction
  } catch (err) {
    ElMessage.error(err.response?.data?.error || '预测失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.card-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* form label with sub-note */
.form-label {
  display: flex;
  align-items: baseline;
  gap: 4px;
  font-size: 13px;
}
.form-label em {
  font-style: normal;
  font-size: 11px;
  color: #94a3b8;
}

/* Result hero */
.result-wrap { padding: 8px 0; }

.result-hero {
  text-align: center;
  padding: 28px 0 20px;
}
.result-hero-label {
  font-size: 13px;
  color: #94a3b8;
  margin-bottom: 10px;
  font-weight: 500;
}
.result-hero-value {
  font-size: 56px;
  font-weight: 800;
  color: #409EFF;
  line-height: 1;
  letter-spacing: -0.03em;
}
.result-hero-sub {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  margin-top: 12px;
  font-size: 12px;
  color: #94a3b8;
}

/* Param grid */
.param-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px 24px;
  padding: 4px 0;
}
.param-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 7px;
  border: 1px solid #e2e8f0;
}
.param-label { font-size: 12px; color: #94a3b8; }
.param-value { font-size: 13px; font-weight: 600; color: #334155; }

/* Empty state */
.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  gap: 14px;
  color: #cbd5e1;
}
.empty-hint p { margin: 0; font-size: 14px; }
</style>
