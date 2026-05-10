<template>
  <div>
    <!-- KPI 卡片 -->
    <el-row :gutter="16" class="kpi-row">
      <el-col :span="6" v-for="card in statCards" :key="card.label">
        <div class="kpi-card" v-loading="loading">
          <div class="kpi-icon" :style="{ background: card.bg }">
            <el-icon size="20" color="#fff"><component :is="card.icon" /></el-icon>
          </div>
          <div class="kpi-body">
            <div class="kpi-value">{{ card.value?.toLocaleString() ?? '—' }}</div>
            <div class="kpi-label">{{ card.label }}</div>
          </div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表 -->
    <el-card style="margin-bottom:20px" v-loading="loading">
      <template #header>
        <div class="card-header-row">
          <span>点赞数量 TOP10 视频</span>
          <el-tag size="small" type="info">按点赞数降序</el-tag>
        </div>
      </template>
      <div ref="chartRef" style="height:360px"></div>
    </el-card>

    <!-- 视频列表 -->
    <el-card v-loading="tableLoading">
      <template #header>
        <div class="card-header-row">
          <span>视频数据列表</span>
          <div style="display:flex;align-items:center;gap:10px">
            <el-select v-model="sortBy" size="small" style="width:130px" @change="loadVideos(1)">
              <el-option label="点赞数降序"   value="likeCount"    />
              <el-option label="评论数降序"   value="commentCount" />
              <el-option label="分享数降序"   value="shareCount"   />
              <el-option label="发布时间降序" value="publishTime"  />
            </el-select>
            <el-tag size="small" type="info">共 {{ total }} 条</el-tag>
          </div>
        </div>
      </template>

      <el-table :data="videos" border stripe size="small" style="width:100%">
        <el-table-column prop="username"    label="用户名"   width="110" />
        <el-table-column prop="description" label="视频描述" min-width="200" show-overflow-tooltip />
        <el-table-column prop="publishTime" label="发布时间" width="108" />
        <el-table-column prop="duration"    label="时长(s)"  width="80"  align="right" />
        <el-table-column prop="likeCount"    label="点赞"    width="90"  align="right" sortable />
        <el-table-column prop="collectCount" label="收藏"    width="90"  align="right" sortable />
        <el-table-column prop="commentCount" label="评论"    width="90"  align="right" sortable />
        <el-table-column prop="shareCount"   label="分享"    width="90"  align="right" sortable />
        <el-table-column prop="fansCount"    label="粉丝"    width="100" align="right" sortable />
        <el-table-column label="原视频" width="80" align="center" fixed="right">
          <template #default="{ row }">
            <a v-if="row.aweme_id" :href="`https://www.douyin.com/video/${row.aweme_id}`" target="_blank" rel="noopener">
              <el-button size="small" type="primary" link>跳转</el-button>
            </a>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-bar">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="10"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadVideos"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const loading      = ref(false)
const tableLoading = ref(false)
const stats        = ref({})
const videos       = ref([])
const total        = ref(0)
const currentPage  = ref(1)
const sortBy       = ref('likeCount')
const chartRef     = ref(null)
let chart = null

const statCards = computed(() => [
  { label: '视频总数', value: stats.value.total,         icon: 'VideoPlay',    bg: 'linear-gradient(135deg,#409EFF,#337ecc)' },
  { label: '点赞总数', value: stats.value.total_like,    icon: 'Promotion',    bg: 'linear-gradient(135deg,#ef4444,#dc2626)' },
  { label: '评论总数', value: stats.value.total_comment, icon: 'ChatDotRound', bg: 'linear-gradient(135deg,#f59e0b,#d97706)' },
  { label: '收藏总数', value: stats.value.total_collect, icon: 'Star',         bg: 'linear-gradient(135deg,#10b981,#059669)' },
])

async function loadDashboard() {
  loading.value = true
  try {
    const res = await api.get('/dashboard/')
    stats.value = res.data.stats
    const tv = res.data.top_videos

    await nextTick()
    if (chart) chart.dispose()
    chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'shadow' },
        backgroundColor: '#fff',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        textStyle: { color: '#334155', fontSize: 13 },
      },
      legend: { data: ['点赞数', '收藏数'], top: 4, right: 10, itemHeight: 10 },
      grid: { left: 0, right: 16, bottom: 0, top: 36, containLabel: true },
      xAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#f1f5f9' } } },
      yAxis: {
        type: 'category',
        inverse: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { fontSize: 12, color: '#475569' },
        data: tv.descriptions.map(d => d?.length > 14 ? d.slice(0, 14) + '…' : d),
      },
      series: [
        {
          name: '点赞数', type: 'bar', barMaxWidth: 20,
          data: tv.like_counts,
          itemStyle: { color: new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#409EFF'},{offset:1,color:'#60b4ff'}]), borderRadius:[0,4,4,0] },
          label: { show: true, position: 'right', fontSize: 11, color: '#94a3b8' },
        },
        {
          name: '收藏数', type: 'bar', barMaxWidth: 20,
          data: tv.collect_counts,
          itemStyle: { color: new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#10b981'},{offset:1,color:'#34d399'}]), borderRadius:[0,4,4,0] },
          label: { show: true, position: 'right', fontSize: 11, color: '#94a3b8' },
        },
      ],
    })
  } finally {
    loading.value = false
  }
}

async function loadVideos(page = 1) {
  tableLoading.value = true
  try {
    const res = await api.get('/videos/', { params: { page, sort: sortBy.value } })
    videos.value      = res.data.results
    total.value       = res.data.count
    currentPage.value = res.data.current_page
  } finally {
    tableLoading.value = false
  }
}

onMounted(() => { loadDashboard(); loadVideos() })
onUnmounted(() => chart?.dispose())
</script>

<style scoped>
/* KPI cards */
.kpi-row { margin-bottom: 20px; }

.kpi-card {
  background: #fff;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 4px rgba(0,0,0,0.07);
  padding: 18px 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: box-shadow 0.2s, transform 0.2s;
}
.kpi-card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  transform: translateY(-1px);
}
.kpi-icon {
  width: 46px; height: 46px;
  border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.kpi-value {
  font-size: 26px;
  font-weight: 700;
  color: #0f172a;
  line-height: 1;
  letter-spacing: -0.02em;
}
.kpi-label {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 5px;
  font-weight: 500;
}

/* Card header row */
.card-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* Table */
.text-muted { color: #cbd5e1; }

/* Pagination */
.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
