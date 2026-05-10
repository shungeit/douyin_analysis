<template>
  <div>
    <el-alert
      title="以下操作会修改数据库或覆盖文件，请在确认后执行。"
      type="warning" show-icon :closable="false"
      style="margin-bottom:16px"
    />

    <el-row :gutter="16">

      <!-- ── AI 配置 ── -->
      <el-col :span="12" style="margin-bottom:16px">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="op-index" style="background:#9B59B6">AI</span>
              <b>AI 模型配置</b>
              <StatusTag :status="cfgStatus.ai" />
            </div>
          </template>
          <el-form :model="aiCfg" label-width="82px" size="small">
            <el-form-item label="模型名称">
              <el-input v-model="aiCfg.ai_model" placeholder="如：ernie-3.5-8k" />
            </el-form-item>
            <el-form-item label="API Key">
              <el-input v-model="aiCfg.ai_api_key" type="password" show-password placeholder="bce-v3/..." />
            </el-form-item>
            <el-form-item label="接口地址">
              <el-input v-model="aiCfg.ai_base_url" placeholder="https://..." />
            </el-form-item>
            <el-form-item label="App ID">
              <el-input v-model="aiCfg.ai_appid" placeholder="app-xxxxxxxx" />
            </el-form-item>
          </el-form>
          <el-button type="primary" size="small" :loading="cfgStatus.ai==='loading'" @click="saveCfg('ai')">
            <el-icon><Check /></el-icon> 保存配置
          </el-button>
        </el-card>
      </el-col>

      <!-- ── 源数据库配置 ── -->
      <el-col :span="12" style="margin-bottom:16px">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="op-index" style="background:#27AE60">DB</span>
              <b>源数据库配置</b>
              <StatusTag :status="cfgStatus.src" />
            </div>
          </template>
          <el-form :model="srcCfg" label-width="82px" size="small">
            <el-form-item label="Host / IP">
              <el-input v-model="srcCfg.src_db_host" placeholder="192.168.1.x" />
            </el-form-item>
            <el-form-item label="端口">
              <el-input-number v-model="srcCfg.src_db_port" :min="1" :max="65535" style="width:100%" />
            </el-form-item>
            <el-form-item label="数据库名">
              <el-input v-model="srcCfg.src_db_name" placeholder="media_crawler" />
            </el-form-item>
            <el-form-item label="账号">
              <el-input v-model="srcCfg.src_db_user" placeholder="root" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input v-model="srcCfg.src_db_password" type="password" show-password placeholder="数据库密码" />
            </el-form-item>
          </el-form>
          <el-button type="primary" size="small" :loading="cfgStatus.src==='loading'" @click="saveCfg('src')">
            <el-icon><Check /></el-icon> 保存配置
          </el-button>
        </el-card>
      </el-col>

      <!-- ── 01 全量数据迁移 ── -->
      <el-col :span="24" style="margin-bottom:16px">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="op-index">01</span>
              <b>全量数据迁移</b>
              <StatusTag :status="ops.migrate.status" />
            </div>
          </template>

          <p class="op-desc">
            从已保存的源数据库（<code>{{ srcCfg.src_db_name || 'media_crawler' }}</code>）读取视频和评论，
            写入当前业务库 <code>dy_django_analysis</code>。
            连接配置请在上方「源数据库配置」中修改并保存。
          </p>
          <el-switch v-model="ops.migrate.clear" active-text="清空后迁移" inactive-text="追加模式" style="margin-bottom:12px" />

          <div v-if="ops.migrate.message" class="op-result" :class="ops.migrate.status">
            <el-icon v-if="ops.migrate.status==='success'"><CircleCheck /></el-icon>
            <el-icon v-else-if="ops.migrate.status==='error'"><CircleClose /></el-icon>
            {{ ops.migrate.message }}
            <span v-if="ops.migrate.videos != null" class="op-detail">
              (视频 {{ ops.migrate.videos }} 条 / 评论 {{ ops.migrate.comments }} 条)
            </span>
          </div>
          <el-button type="primary" :loading="ops.migrate.status==='loading'"
            :disabled="ops.migrate.status==='loading'" @click="run('migrate')">
            <el-icon><Upload /></el-icon> 开始迁移
          </el-button>
        </el-card>
      </el-col>

      <!-- ── 02 刷新统计表 ── -->
      <el-col :span="12" style="margin-bottom:16px">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="op-index">02</span><b>刷新统计表</b>
              <StatusTag :status="ops.stats.status" />
            </div>
          </template>
          <p class="op-desc">重新计算 <code>part1~part5</code> 预计算表，各图表页即时更新。</p>
          <div v-if="ops.stats.message" class="op-result" :class="ops.stats.status">
            <el-icon v-if="ops.stats.status==='success'"><CircleCheck /></el-icon>
            <el-icon v-else-if="ops.stats.status==='error'"><CircleClose /></el-icon>
            {{ ops.stats.message }}
          </div>
          <el-button type="primary" :loading="ops.stats.status==='loading'"
            :disabled="ops.stats.status==='loading'" @click="run('stats')">
            <el-icon><Refresh /></el-icon> 刷新统计
          </el-button>
        </el-card>
      </el-col>

      <!-- ── 03 NLP ── -->
      <el-col :span="12" style="margin-bottom:16px">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="op-index">03</span><b>NLP 情感分析</b>
              <StatusTag :status="ops.nlp.status" />
            </div>
          </template>
          <p class="op-desc">
            对全部评论重跑 SnowNLP + jieba，结果写入 <code>nlp_result.csv</code>。
            <br /><el-text type="warning" size="small">评论较多时约需 30~60 秒</el-text>
          </p>
          <div v-if="ops.nlp.status==='loading'" class="op-result loading">
            <el-icon class="is-loading"><Loading /></el-icon>
            正在分析中，请耐心等待（可能需要 30~60 秒）…
          </div>
          <div v-else-if="ops.nlp.message" class="op-result" :class="ops.nlp.status">
            <el-icon v-if="ops.nlp.status==='success'"><CircleCheck /></el-icon>
            <el-icon v-else-if="ops.nlp.status==='error'"><CircleClose /></el-icon>
            {{ ops.nlp.message }}
            <span v-if="ops.nlp.positive != null" class="op-detail">
              (积极 {{ ops.nlp.positive }} / 消极 {{ ops.nlp.negative }} / 中性 {{ ops.nlp.neutral }})
            </span>
          </div>
          <el-button type="primary" :loading="ops.nlp.status==='loading'"
            :disabled="ops.nlp.status==='loading'" @click="run('nlp')">
            <el-icon><DataAnalysis /></el-icon> 运行 NLP
          </el-button>
        </el-card>
      </el-col>

      <!-- ── 04 词云 ── -->
      <el-col :span="12" style="margin-bottom:16px">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="op-index">04</span><b>重新生成词云图</b>
              <StatusTag :status="ops.wordcloud.status" />
            </div>
          </template>
          <p class="op-desc">
            基于当前数据库内容重新生成 <code>title_wordcloud.jpg</code> 和
            <code>comment_wordcloud.jpg</code>。
          </p>
          <div v-if="ops.wordcloud.message" class="op-result" :class="ops.wordcloud.status">
            <el-icon v-if="ops.wordcloud.status==='success'"><CircleCheck /></el-icon>
            <el-icon v-else-if="ops.wordcloud.status==='error'"><CircleClose /></el-icon>
            {{ ops.wordcloud.message }}
          </div>
          <el-button type="primary" :loading="ops.wordcloud.status==='loading'"
            :disabled="ops.wordcloud.status==='loading'" @click="run('wordcloud')">
            <el-icon><Picture /></el-icon> 生成词云
          </el-button>
        </el-card>
      </el-col>

    </el-row>
  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api, { apiLong } from '@/api'

// ── AI 配置 ──
const aiCfg = reactive({ ai_model: '', ai_api_key: '', ai_base_url: '', ai_appid: '' })
// ── 源库配置 ──
const srcCfg = reactive({ src_db_host: '', src_db_port: 3306, src_db_name: 'media_crawler', src_db_user: '', src_db_password: '' })
// ── 配置保存状态 ──
const cfgStatus = reactive({ ai: 'idle', src: 'idle' })

// ── 操作状态 ──
const ops = reactive({
  migrate:   { status:'idle', message:'', clear:false, videos:null, comments:null },
  stats:     { status:'idle', message:'' },
  nlp:       { status:'idle', message:'', positive:null, negative:null, neutral:null },
  wordcloud: { status:'idle', message:'' },
})

async function loadConfig() {
  try {
    const res = await api.get('/config/')
    const d = res.data
    aiCfg.ai_model    = d.ai_model    || ''
    aiCfg.ai_api_key  = d.ai_api_key  || ''
    aiCfg.ai_base_url = d.ai_base_url || ''
    aiCfg.ai_appid    = d.ai_appid    || ''
    srcCfg.src_db_host     = d.src_db_host     || ''
    srcCfg.src_db_port     = parseInt(d.src_db_port || 3306)
    srcCfg.src_db_name     = d.src_db_name     || 'media_crawler'
    srcCfg.src_db_user     = d.src_db_user     || ''
    srcCfg.src_db_password = d.src_db_password || ''
  } catch { /* ignore */ }
}

async function saveCfg(type) {
  cfgStatus[type] = 'loading'
  const payload = type === 'ai' ? { ...aiCfg } : { ...srcCfg }
  try {
    const res = await api.post('/config/', payload)
    if (res.data.success) {
      cfgStatus[type] = 'success'
      ElMessage.success(res.data.message || '配置已保存')
    }
  } catch (err) {
    cfgStatus[type] = 'error'
    ElMessage.error(err.response?.data?.message || '保存失败')
  }
}

const opConfig = {
  migrate: {
    url: '/ops/migrate/',
    payload: () => ({
      clear: ops.migrate.clear,
    }),
    confirmMsg: o => o.clear ? '将清空现有数据后重新导入，确认？' : '将追加写入数据，确认？',
    onSuccess:  (d, o) => { o.message = d.message; o.videos = d.videos; o.comments = d.comments },
  },
  stats: {
    url:'/ops/refresh-stats/', payload:()=>({}),
    confirmMsg: ()=>'将重新计算 part1~part5 统计表，确认？',
    onSuccess: (d,o)=>{ o.message = d.message },
  },
  nlp: {
    url:'/ops/nlp/', payload:()=>({}), long: true,
    confirmMsg: ()=>'将对全部评论重跑情感分析（评论较多时约需 30~60 秒），确认？',
    onSuccess: (d,o)=>{ o.message=d.message; o.positive=d.positive; o.negative=d.negative; o.neutral=d.neutral },
  },
  wordcloud: {
    url:'/ops/wordcloud/', payload:()=>({}), long: true,
    confirmMsg: ()=>'将覆盖现有词云图文件，确认？',
    onSuccess: (d,o)=>{ o.message=d.message },
  },
}

async function run(key) {
  const op = ops[key]; const cfg = opConfig[key]
  try {
    await ElMessageBox.confirm(cfg.confirmMsg(op), '确认操作', { type:'warning', confirmButtonText:'确认', cancelButtonText:'取消' })
  } catch { return }
  op.status = 'loading'; op.message = ''
  const request = cfg.long ? apiLong() : api
  try {
    const res = await request.post(cfg.url, cfg.payload())
    if (res.data.success) { op.status='success'; cfg.onSuccess(res.data, op); ElMessage.success(res.data.message) }
    else                  { op.status='error';   op.message=res.data.message; ElMessage.error(res.data.message) }
  } catch (err) {
    op.status='error'; op.message=err.response?.data?.message||'请求失败'; ElMessage.error(op.message)
  }
}

onMounted(loadConfig)
</script>

<script>
export default {
  components: {
    StatusTag: {
      props: ['status'],
      template: `<el-tag size="small" :type="map[status]?.type" style="margin-left:8px">{{ map[status]?.label }}</el-tag>`,
      data: () => ({ map: { idle:{type:'info',label:'待执行'}, loading:{type:'warning',label:'执行中'}, success:{type:'success',label:'成功'}, error:{type:'danger',label:'失败'} } }),
    },
  },
}
</script>

<style scoped>
.card-header { display:flex; align-items:center; gap:8px; }
.op-index {
  display:inline-flex; align-items:center; justify-content:center;
  width:28px; height:22px; background:#409EFF; color:#fff;
  border-radius:6px; font-size:12px; font-weight:700; flex-shrink:0;
}
.op-desc { color:#666; font-size:13px; line-height:1.7; margin-bottom:14px; }
.op-result {
  display:flex; align-items:center; gap:6px; font-size:13px;
  padding:8px 12px; border-radius:6px; margin-bottom:14px;
}
.op-result.success { background:#f0f9eb; color:#67C23A; }
.op-result.error   { background:#fef0f0; color:#F56C6C; }
.op-result.loading { background:#fdf6ec; color:#E6A23C; }
.op-detail { color:#999; margin-left:4px; }
</style>
