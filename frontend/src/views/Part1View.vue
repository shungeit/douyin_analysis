<template>
  <el-card v-loading="loading">
    <template #header>
      <div class="card-header-row">
        <div class="card-title">
          <el-icon style="color:#409EFF"><MapLocation /></el-icon>
          评论用户 IP 地区分布 TOP15
        </div>
        <el-tag size="small" type="info">按评论数降序</el-tag>
      </div>
    </template>
    <div ref="chartRef" style="height:480px"></div>
  </el-card>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import api from '@/api'

const loading  = ref(false)
const chartRef = ref(null)
let chart = null

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/charts/ip-distribution/')
    const sorted = [...res.data.data].sort((a, b) => b.value - a.value).slice(0, 15)
    await nextTick()
    chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: {
        trigger: 'axis',
        backgroundColor: '#fff',
        borderColor: '#e2e8f0',
        borderWidth: 1,
        textStyle: { color: '#334155', fontSize: 13 },
      },
      grid: { left: 0, right: 20, bottom: 0, top: 12, containLabel: true },
      xAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#f1f5f9' } } },
      yAxis: {
        type: 'category',
        inverse: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { fontSize: 12, color: '#475569' },
        data: sorted.map(d => d.name),
      },
      series: [{
        type: 'bar',
        barMaxWidth: 22,
        data: sorted.map(d => d.value),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(1,0,0,0,[
            { offset: 0, color: '#409EFF' },
            { offset: 1, color: '#85c5ff' },
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
onUnmounted(() => chart?.dispose())
</script>

<style scoped>
.card-header-row { display: flex; align-items: center; justify-content: space-between; }
.card-title { display: flex; align-items: center; gap: 7px; }
</style>
