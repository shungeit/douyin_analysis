<template>
  <div>
    <!-- 视频选择 -->
    <el-card style="margin-bottom:16px">
      <template #header><b>选择视频</b></template>
      <el-table
        :data="videos"
        highlight-current-row
        @current-change="selectVideo"
        size="small"
        border
        v-loading="tableLoading"
      >
        <el-table-column prop="username" label="用户名" width="110" />
        <el-table-column prop="description" label="视频描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="publishTime" label="发布时间" width="110" />
        <el-table-column prop="likeCount" label="点赞" width="90" />
        <el-table-column prop="fansCount" label="粉丝" width="100" />
      </el-table>
      <div class="pagination">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="10"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadVideos"
        />
      </div>
    </el-card>

    <!-- 分析面板 -->
    <el-row :gutter="16">
      <!-- 左：参数 -->
      <el-col :span="9">
        <el-card style="height:100%">
          <template #header><b>分析参数</b></template>
          <template v-if="form">
            <el-form :model="form" label-width="88px" size="small">
              <el-form-item label="视频描述">
                <el-input v-model="form.description" type="textarea" :rows="3" />
              </el-form-item>
              <el-form-item label="发布时间">
                <el-input v-model="form.publish_date" placeholder="YYYY.MM.DD" />
              </el-form-item>
              <el-form-item label="视频时长(秒)">
                <el-input v-model="form.duration" placeholder="如：15" />
              </el-form-item>
              <el-form-item label="粉丝数量">
                <el-input-number v-model="form.fans" :min="0" style="width:100%" />
              </el-form-item>
              <el-form-item label="点赞数量">
                <el-input-number v-model="form.likes" :min="0" style="width:100%" />
              </el-form-item>
              <el-form-item label="收藏数量">
                <el-input-number v-model="form.favorites" :min="0" style="width:100%" />
              </el-form-item>
              <el-form-item label="评论数量">
                <el-input-number v-model="form.comments" :min="0" style="width:100%" />
              </el-form-item>
              <el-form-item label="分享数量">
                <el-input-number v-model="form.shares" :min="0" style="width:100%" />
              </el-form-item>
              <el-form-item label="分析重点">
                <el-input v-model="form.analysis_focus" type="textarea" :rows="2"
                  placeholder="留空使用默认分析维度" />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" :loading="analyzing" @click="analyze" style="width:100%">
                  <el-icon><MagicStick /></el-icon>&nbsp;开始 AI 分析
                </el-button>
              </el-form-item>
            </el-form>
          </template>
          <el-empty v-else description="请先在上方表格中点击一行视频" />
        </el-card>
      </el-col>

      <!-- 右：AI 结果 -->
      <el-col :span="15">
        <el-card class="result-card" style="min-height:480px">
          <template #header>
            <div class="result-header">
              <span><b>AI 分析结果</b></span>
              <div v-if="metrics" class="metrics-bar">
                <span class="metric-badge blue">
                  <el-icon><TrendCharts /></el-icon>
                  互动率 {{ metrics.interaction_rate?.toFixed(2) }}%
                </span>
                <span class="metric-badge green">
                  <el-icon><Promotion /></el-icon>
                  点赞率 {{ metrics.like_rate?.toFixed(2) }}%
                </span>
                <span v-if="metrics.duration" class="metric-badge gray">
                  <el-icon><VideoPlay /></el-icon>
                  {{ metrics.duration }}秒
                </span>
              </div>
            </div>
          </template>

          <!-- 分析中 -->
          <div v-if="analyzing" class="analyzing-state">
            <div class="pulse-ring"></div>
            <el-icon class="spin-icon"><Loading /></el-icon>
            <p>AI 正在分析，请稍候…</p>
          </div>

          <!-- 结果 -->
          <div v-else-if="analysis" class="analysis-body" v-html="renderedAnalysis" />

          <!-- 空 -->
          <div v-else class="empty-state">
            <el-icon size="48" color="#ddd"><MagicStick /></el-icon>
            <p>选择视频并点击「开始 AI 分析」</p>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const tableLoading = ref(false)
const analyzing    = ref(false)
const videos       = ref([])
const total        = ref(0)
const currentPage  = ref(1)
const analysis     = ref('')
const metrics      = ref(null)
const form         = ref(null)

async function loadVideos(page = 1) {
  tableLoading.value = true
  try {
    const res = await api.get('/videos/', { params: { page } })
    videos.value      = res.data.results
    total.value       = res.data.count
    currentPage.value = res.data.current_page
  } finally {
    tableLoading.value = false
  }
}

function selectVideo(row) {
  if (!row) return
  form.value = reactive({
    fans:           row.fansCount    || 0,
    publish_date:   row.publishTime  || '',
    description:    row.description  || '',
    duration:       row.duration     || 0,
    likes:          row.likeCount    || 0,
    favorites:      row.collectCount || 0,
    comments:       row.commentCount || 0,
    shares:         row.shareCount   || 0,
    analysis_focus: '',
  })
  analysis.value = ''
  metrics.value  = null
}

async function analyze() {
  if (!form.value) return
  analyzing.value = true
  analysis.value  = ''
  metrics.value   = null
  try {
    const res = await api.post('/ai/analyze/', form.value)
    if (res.data.error) {
      ElMessage.error(res.data.error)
    } else {
      analysis.value = res.data.analysis
      metrics.value  = res.data.metrics
    }
  } catch {
    ElMessage.error('AI 分析请求失败')
  } finally {
    analyzing.value = false
  }
}

// 将 AI 文本转换为结构化 HTML
const renderedAnalysis = computed(() => {
  if (!analysis.value) return ''
  const lines = analysis.value.split('\n')
  let html = ''
  let listOpen = false

  const closelist = () => { if (listOpen) { html += '</ul>'; listOpen = false } }

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i]
    const line = raw.trim()

    // === Section Title ===
    const secMatch = line.match(/^===\s*(.+?)\s*===$/)
    if (secMatch) {
      closelist()
      html += `<div class="ai-section"><el-icon></el-icon>${secMatch[1]}</div>`
      continue
    }

    // empty
    if (!line) { closelist(); continue }

    // numbered: 1. **title**
    const numMatch = line.match(/^(\d+)\.\s+(.+)/)
    if (numMatch) {
      closelist()
      const content = renderInline(numMatch[2])
      html += `<div class="ai-numbered"><span class="num">${numMatch[1]}</span><div>${content}</div></div>`
      continue
    }

    // bullet: - text or • text
    if (/^[-•]\s/.test(line)) {
      if (!listOpen) { html += '<ul class="ai-list">'; listOpen = true }
      html += `<li>${renderInline(line.slice(2))}</li>`
      continue
    }

    closelist()
    html += `<p class="ai-para">${renderInline(line)}</p>`
  }
  closelist()
  return html
})

function renderInline(text) {
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
}

onMounted(loadVideos)
</script>

<style scoped>
.pagination { margin-top: 12px; display: flex; justify-content: flex-end; }

/* 结果卡片 header */
.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}
.metrics-bar { display: flex; gap: 8px; flex-wrap: wrap; }
.metric-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
}
.metric-badge.blue  { background: #ecf5ff; color: #409EFF; }
.metric-badge.green { background: #f0f9eb; color: #67C23A; }
.metric-badge.gray  { background: #f4f4f5; color: #909399; }

/* 加载动画 */
.analyzing-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: #409EFF;
  gap: 12px;
  position: relative;
}
.analyzing-state p { margin: 0; font-size: 14px; color: #666; }
.pulse-ring {
  position: absolute;
  width: 56px; height: 56px;
  border-radius: 50%;
  border: 3px solid #409EFF;
  animation: pulse 1.4s ease-out infinite;
  opacity: 0;
}
.spin-icon { font-size: 32px; animation: spin 1s linear infinite; }
@keyframes pulse {
  0%   { transform: scale(0.8); opacity: 0.8; }
  100% { transform: scale(1.8); opacity: 0; }
}
@keyframes spin { to { transform: rotate(360deg); } }

/* 空状态 */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 60px 0; color: #bbb; gap: 12px;
}
.empty-state p { margin: 0; font-size: 13px; }

/* 分析内容 */
.analysis-body { padding: 4px 0; line-height: 1.8; color: #333; }

/* Section header */
:deep(.ai-section) {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 700;
  color: #409EFF;
  margin: 20px 0 10px;
  padding-bottom: 6px;
  border-bottom: 2px solid #ecf5ff;
}
:deep(.ai-section):first-child { margin-top: 4px; }

/* numbered item */
:deep(.ai-numbered) {
  display: flex;
  gap: 10px;
  margin: 10px 0 6px;
  align-items: flex-start;
}
:deep(.ai-numbered .num) {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 22px; height: 22px;
  background: #409EFF;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 2px;
}
:deep(.ai-numbered div) { flex: 1; }

/* bullet list */
:deep(.ai-list) {
  margin: 6px 0;
  padding-left: 0;
  list-style: none;
}
:deep(.ai-list li) {
  position: relative;
  padding: 4px 0 4px 20px;
  font-size: 14px;
  color: #555;
}
:deep(.ai-list li::before) {
  content: '';
  position: absolute;
  left: 4px; top: 13px;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #67C23A;
}

/* paragraph */
:deep(.ai-para) {
  margin: 6px 0;
  font-size: 14px;
  color: #444;
}

:deep(strong) { color: #303133; }
:deep(code) {
  background: #f5f7fa;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 13px;
  color: #e6522c;
}
</style>
