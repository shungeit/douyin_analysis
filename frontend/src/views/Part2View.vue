<template>
  <el-row :gutter="16">
    <el-col :span="10">
      <el-card v-loading="loading">
        <template #header>
          <div class="card-title"><el-icon style="color:#10b981"><UserFilled /></el-icon>粉丝数量区间分布</div>
        </template>
        <div ref="pieRef" style="height:380px"></div>
      </el-card>
    </el-col>
    <el-col :span="14">
      <el-card v-loading="loading">
        <template #header>
          <div class="card-header-row">
            <div class="card-title"><el-icon style="color:#409EFF"><TrendCharts /></el-icon>粉丝数量 TOP10 博主</div>
            <el-tag size="small" type="info">按粉丝数降序</el-tag>
          </div>
        </template>
        <div ref="barRef" style="height:380px"></div>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const loading = ref(false)
const pieRef  = ref(null)
const barRef  = ref(null)
let pieChart = null
let barChart = null

const PIE_COLORS = ['#409EFF','#10b981','#f59e0b','#ef4444','#8b5cf6','#06b6d4']

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/charts/fans-distribution/')
    const { fans_range, top10 } = res.data
    const topBloggers = top10.names
      .map((name, i) => ({ name, value: top10.values[i] }))
      .sort((a, b) => b.value - a.value)

    await nextTick()

    pieChart = echarts.init(pieRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', backgroundColor: '#fff', borderColor: '#e2e8f0', borderWidth: 1 },
      legend: { bottom: '2%', textStyle: { fontSize: 12, color: '#475569' } },
      series: [{
        type: 'pie',
        radius: ['42%', '70%'],
        padAngle: 3,
        data: fans_range.map((d, i) => ({ ...d, itemStyle: { color: PIE_COLORS[i % PIE_COLORS.length] } })),
        label: { formatter: '{b}\n{d}%', fontSize: 12 },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.15)' } },
      }],
    })

    barChart = echarts.init(barRef.value)
    barChart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#e2e8f0', borderWidth: 1 },
      grid: { left: 0, right: 20, bottom: 0, top: 10, containLabel: true },
      xAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#f1f5f9' } } },
      yAxis: {
        type: 'category',
        inverse: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { fontSize: 12, color: '#475569' },
        data: topBloggers.map(d => d.name),
      },
      series: [{
        type: 'bar',
        barMaxWidth: 22,
        data: topBloggers.map(d => d.value),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1,0,0,0,[
            { offset: 0, color: '#10b981' },
            { offset: 1, color: '#6ee7b7' },
          ]),
          borderRadius: [0, 5, 5, 0],
        },
        label: { show: true, position: 'right', fontSize: 11, color: '#94a3b8' },
      }],
    })
  } finally {
    loading.value = false
  }
})
onUnmounted(() => { pieChart?.dispose(); barChart?.dispose() })
</script>

<style scoped>
.card-header-row { display: flex; align-items: center; justify-content: space-between; }
.card-title { display: flex; align-items: center; gap: 7px; }
</style>
