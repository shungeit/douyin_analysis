<template>
  <el-card v-loading="loading">
    <template #header>
      <div class="header-row">
        <span>评论数据列表</span>
        <div class="header-tools">
          <el-input
            v-model="search"
            placeholder="搜索评论内容 / 用户名"
            clearable
            size="small"
            style="width:220px"
            :prefix-icon="Search"
            @input="onSearch"
          />
          <el-tag size="small" type="info">共 {{ total }} 条</el-tag>
        </div>
      </div>
    </template>

    <el-table :data="comments" border stripe size="small" style="width:100%">
      <el-table-column type="index" label="#" width="52" align="center" />
      <el-table-column prop="username"    label="用户名"   width="120" />
      <el-table-column prop="content"     label="评论内容" min-width="260" show-overflow-tooltip />
      <el-table-column prop="commentTime" label="评论时间" width="155" />
      <el-table-column prop="userIP"      label="IP 属地"  width="100" />
      <el-table-column prop="likeCount"   label="点赞数"   width="90"  align="right" sortable />
      <el-table-column prop="aweme_id"    label="视频 ID"  width="160" show-overflow-tooltip />
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="10"
        :total="total"
        layout="total, prev, pager, next"
        @current-change="load"
      />
    </div>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import api from '@/api'

const loading     = ref(false)
const comments    = ref([])
const total       = ref(0)
const currentPage = ref(1)
const search      = ref('')
let searchTimer   = null

async function load(page = 1) {
  loading.value = true
  try {
    const res = await api.get('/comments/', { params: { page, search: search.value || undefined } })
    comments.value    = res.data.results
    total.value       = res.data.count
    currentPage.value = res.data.current_page
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => load(1), 400)
}

onMounted(load)
</script>

<style scoped>
.header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.header-tools {
  display: flex;
  align-items: center;
  gap: 10px;
}
.pagination-bar {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}
</style>
