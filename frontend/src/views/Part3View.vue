<template>
  <div>
    <el-card v-loading="loading" style="margin-bottom:16px">
      <template #header>
        <div class="card-header-row">
          <div class="card-title"><el-icon style="color:#5470c6"><TrendCharts /></el-icon>评论量 / 分享量 TOP10 视频</div>
          <el-tag size="small" type="info">按评论+分享总量降序</el-tag>
        </div>
      </template>
      <div ref="barRef" style="height:380px"></div>
    </el-card>

    <el-card v-loading="loading">
      <template #header>
        <div class="card-title"><el-icon style="color:#f59e0b"><Comment /></el-icon>评论高频词汇</div>
      </template>
      <div ref="wordRef" style="height:420px"></div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import api from '@/api'

const loading = ref(false)
const barRef  = ref(null)
const wordRef = ref(null)
let barChart = null
let wordChart = null

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/charts/engagement/')
    const { top10, word_counts } = res.data

    await nextTick()

    barChart = echarts.init(barRef.value)
    barChart.setOption({
      tooltip: { trigger: 'axis', backgroundColor: '#fff', borderColor: '#e2e8f0', borderWidth: 1 },
      legend: { data: ['评论数', '分享数'], top: 4, right: 10, itemHeight: 10 },
      grid: { left: 0, right: 20, bottom: 0, top: 36, containLabel: true },
      xAxis: { type: 'value', axisLine: { show: false }, splitLine: { lineStyle: { color: '#f1f5f9' } } },
      yAxis: {
        type: 'category',
        inverse: true,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { fontSize: 12, color: '#475569' },
        data: top10.name_list.map(n => n?.length > 14 ? n.slice(0, 14) + '…' : n),
      },
      series: [
        {
          name: '评论数', type: 'bar', barMaxWidth: 18,
          data: top10.comment_list,
          itemStyle: { color: new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#5470c6'},{offset:1,color:'#8fa8e8'}]), borderRadius:[0,4,4,0] },
          label: { show: true, position: 'right', fontSize: 11, color: '#94a3b8' },
        },
        {
          name: '分享数', type: 'bar', barMaxWidth: 18,
          data: top10.share_list,
          itemStyle: { color: new echarts.graphic.LinearGradient(1,0,0,0,[{offset:0,color:'#ee6666'},{offset:1,color:'#f5a0a0'}]), borderRadius:[0,4,4,0] },
          label: { show: true, position: 'right', fontSize: 11, color: '#94a3b8' },
        },
      ],
    })

    if (word_counts.length) {
      wordChart = echarts.init(wordRef.value)
      wordChart.setOption({
        series: [{
          type: 'wordCloud',
          data: word_counts,
          width: '100%', height: '100%',
          gridSize: 8,
          sizeRange: [14, 56],
          rotationRange: [-30, 30],
          textStyle: { color: () => `hsl(${Math.random()*360},60%,50%)` },
          emphasis: { textStyle: { shadowBlur: 8, shadowColor: '#333' } },
        }],
      })
    }
  } finally {
    loading.value = false
  }
})
onUnmounted(() => { barChart?.dispose(); wordChart?.dispose() })
</script>

<style scoped>
.card-header-row { display: flex; align-items: center; justify-content: space-between; }
.card-title { display: flex; align-items: center; gap: 7px; }
</style>
