<template>
  <el-row :gutter="16">
    <el-col :span="10">
      <el-card v-loading="loading">
        <template #header>
          <div class="card-title"><el-icon style="color:#10b981"><Sunny /></el-icon>情感倾向分布</div>
        </template>
        <div ref="pieRef" style="height:380px"></div>
      </el-card>
    </el-col>
    <el-col :span="14">
      <el-card v-loading="loading">
        <template #header>
          <div class="card-title"><el-icon style="color:#5470c6"><DataLine /></el-icon>情感分值区间分布</div>
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

const COLORS = { '积极': '#10b981', '中性': '#f59e0b', '消极': '#ef4444' }

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/charts/sentiment/')
    const { pie_data, distribution } = res.data

    await nextTick()

    pieChart = echarts.init(pieRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)', backgroundColor: '#fff', borderColor: '#e2e8f0', borderWidth: 1 },
      legend: { bottom: '4%', textStyle: { fontSize: 12 } },
      series: [{
        type: 'pie',
        radius: ['44%', '70%'],
        padAngle: 3,
        data: pie_data.map(d => ({ ...d, itemStyle: { color: COLORS[d.name] } })),
        label: { formatter: '{b}\n{d}%', fontSize: 12 },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.15)' } },
      }],
    })

    barChart = echarts.init(barRef.value)
    barChart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#e2e8f0', borderWidth: 1 },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: { type: 'category', data: distribution.names, axisLabel: { fontSize: 11, color: '#475569' } },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#f1f5f9' } } },
      series: [{
        type: 'bar',
        barMaxWidth: 36,
        data: distribution.values,
        itemStyle: {
          borderRadius: [4, 4, 0, 0],
          color: (p) => {
            const score = parseFloat(p.name)
            if (score > 0.5) return '#10b981'
            if (score === 0.5) return '#f59e0b'
            return '#ef4444'
          },
        },
      }],
    })
  } finally {
    loading.value = false
  }
})
onUnmounted(() => { pieChart?.dispose(); barChart?.dispose() })
</script>

<style scoped>
.card-title { display: flex; align-items: center; gap: 7px; }
</style>
