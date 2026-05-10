# 抖音短视频数据分析系统

基于 Django / DRF + Vue 3 + MySQL + ECharts 的抖音短视频数据采集、可视化分析、点赞预测与 AI 智能建议平台。

项目当前同时保留两套前端：

- `frontend/`：Vue 3 + Element Plus 单页应用，推荐作为主入口使用。
- `templates/`：Django 服务端模板旧页面，通过 `/home/` 路由访问，主要用于兼容历史功能。

> **数据说明**：项目默认数据集以关键词 **"哪吒2"** 采集，含视频数据与评论数据，已预置在 `db.sql` 中，开箱即用。

> **默认账号**：`db.sql` 已预置登录账号，用户名 `admin`，密码 `admin`。生产环境部署后请立即修改。

## 业务需求分析

本项目面向短视频内容运营和数据分析场景，核心诉求是把采集到的视频和评论数据转成可读、可比较、可行动的分析结果。

1. **数据接入**：支持使用预置 `db.sql`，也支持从 `media_crawler` 数据库迁移抖音视频与评论数据。
2. **数据管理**：需要维护视频、评论、用户、系统配置等基础数据，并支持刷新统计表、NLP 结果和词云图片。
3. **运营看板**：需要快速看到视频总量、点赞、评论、收藏、热门视频和评论列表。
4. **内容分析**：需要从地区分布、粉丝分布、评论/分享表现、评论情感和词云中判断内容传播特征。
5. **辅助决策**：需要通过点赞预测和 AI 分析，为单条视频给出表现评估与优化建议。
6. **部署演示**：需要能通过 Docker 一键启动，方便课程设计、演示或内网部署。

## 项目架构

```
dy_project/
├── manage.py                  # Django 项目入口
├── config.py                  # 数据库与 API 配置（支持环境变量）
├── util.py                    # 数据库工具类（原生 PyMySQL）
├── forecast.py                # 点赞数预测（加载预训练线性回归模型）
├── Get_Qianfan.py             # 百度千帆大模型分析接口
├── db.sql                     # 数据库初始化脚本（含数据）
├── requirements.txt           # Python 依赖
├── Dockerfile                 # Docker 镜像构建
├── docker-compose.yml         # 一键部署编排
├── entrypoint.sh              # 容器启动脚本
│
├── dy_project/                # Django 项目配置
│   ├── settings.py
│   ├── urls.py                # 路由挂载：/api/、/home/、/admin/
│   ├── wsgi.py
│   └── asgi.py
│
├── video/                     # 核心业务应用
│   ├── models.py              # VideoData / CommentData / SystemConfig / User
│   ├── api.py                 # DRF 接口（认证、看板、图表、预测、AI、数据管理）
│   ├── api_urls.py            # /api/ 路由
│   ├── views.py               # 旧 Django 模板视图
│   ├── urls.py                # /home/ 路由
│   ├── authentication.py      # 基于 session 的 DRF 自定义认证
│   ├── serializers.py         # DRF 序列化器
│   ├── admin.py               # 后台管理配置（SimpleUI）
│   └── migrations/            # 数据库迁移文件
│
├── frontend/                  # Vue 3 单页应用
│   ├── package.json
│   ├── vite.config.js         # 开发环境代理 /api 和 /static
│   ├── nginx.conf             # 生产环境代理 API / 静态资源 / Admin
│   └── src/
│       ├── api/index.js       # Axios 实例
│       ├── router/index.js    # 前端路由与登录守卫
│       ├── store.js           # 用户状态
│       ├── layout/            # 主布局
│       └── views/             # 仪表盘、评论、分析、预测、AI、数据管理
│
├── templates/                 # 旧 Django 前端页面模板
│   ├── base.html              # 基础布局（侧边栏 + 顶栏）
│   ├── login.html / register.html
│   ├── index.html             # 首页仪表盘
│   ├── comment_list.html      # 评论列表
│   ├── get_ai.html            # AI 智能分析
│   ├── predict.html           # 点赞数预测
│   ├── changeInfo.html        # 修改密码
│   ├── part1.html             # 用户 IP 地区分布（地图）
│   ├── part2.html             # 粉丝区间分布 + 粉丝排行
│   ├── part3.html             # 评论量 / 分享量分析
│   ├── part4.html             # 情感分析（积极 / 消极 / 中性）
│   ├── part5.html             # 视频标题词云图
│   └── part6.html             # 评论词云图
│
├── static/                    # 静态资源
│   ├── css/                   # 样式文件（多主题）
│   ├── js/                    # ECharts + 前端脚本
│   ├── fonts/                 # 字体文件
│   ├── img/                   # 图片资源（头像、词云图等）
│   └── vendor/                # Bootstrap 4 / jQuery / Font Awesome
│
├── build_model/               # 机器学习模型
│   ├── build.py               # 模型训练脚本（线性回归）
│   ├── like_model.joblib      # 预训练模型
│   └── like_scaler.joblib     # 特征标准化器
│
└── data/                      # 数据采集与处理（离线脚本）
    ├── spider.py              # 抖音视频数据爬虫
    ├── spider_comment.py      # 抖音评论数据爬虫
    ├── csv_to_sql.py          # CSV 数据导入 MySQL
    ├── migrate_from_mediacrawler.py # 从 media_crawler 迁移数据
    ├── data_analysis.py       # 预计算统计表（part1~part5）
    ├── nlp.py                 # NLP 情感分析（SnowNLP）
    ├── wordCloud.py           # 词云图生成
    ├── data.csv               # 视频原始数据
    ├── comment_data.csv       # 评论原始数据
    └── nlp_result.csv         # NLP 分析结果
```

## 技术栈

| 层级 | 技术 |
|------|------|
| **后端框架** | Django 3.2 + Django REST Framework |
| **数据库** | MySQL 8.0 |
| **后台管理** | Django SimpleUI |
| **新前端** | Vue 3 + Vite + Vue Router + Element Plus + Axios |
| **旧前端** | Django Templates + Bootstrap 4 + jQuery |
| **数据可视化** | ECharts（柱状图、饼图、地图、词云） |
| **机器学习** | scikit-learn（线性回归 — 点赞预测） |
| **NLP** | jieba 分词 + SnowNLP 情感分析 |
| **AI 分析** | 百度千帆大模型（通过 OpenAI 兼容接口调用） |
| **数据采集** | requests（抖音 Web API 爬虫） |
| **部署** | Docker Compose + Nginx |

## 功能模块

1. **用户系统** — 注册、登录、修改密码、退出登录，Vue 前端通过 session 保持登录态
2. **首页仪表盘** — 视频总数 / 点赞总数 / 评论总数 / 收藏总数 + 视频数据表格（分页）
3. **评论管理** — 分页浏览全部评论数据
4. **数据可视化**
   - 用户 IP 地区分布（中国地图热力）
   - 粉丝数量区间分布 + 粉丝排行 TOP10
   - 评论量 / 分享量分析（TOP10 视频对比）
   - 情感分析（积极 / 消极 / 中性饼图 + 情感分值分布）
   - 视频标题词云图 / 评论词云图
5. **点赞数预测** — 输入视频参数，基于线性回归模型预测点赞数
6. **AI 智能分析** — 调用百度千帆大模型分析单条视频数据并给出优化建议
7. **数据管理** — 保存 AI / 源库配置，执行源库迁移、统计刷新、NLP、词云生成
8. **后台管理** — Django Admin + SimpleUI，管理视频、评论、用户数据

## 数据库设计

```
dy_django_analysis
├── videodata          # 视频信息表
│   ├── username       # 博主用户名
│   ├── fansCount      # 粉丝数量
│   ├── description    # 视频描述
│   ├── aweme_id       # 视频 ID
│   ├── publishTime    # 发表时间（格式：YYYY.MM.DD）
│   ├── duration       # 视频时长（格式：MM:SS）
│   ├── likeCount      # 点赞数量
│   ├── collectCount   # 收藏数量
│   ├── commentCount   # 评论数量
│   ├── shareCount     # 分享数量
│   └── downloadCount  # 下载数量
│
├── commentdata        # 评论信息表
│   ├── userid         # 评论用户 ID
│   ├── username       # 评论用户名
│   ├── commentTime    # 评论时间
│   ├── userIP         # 归属地（IP 属地）
│   ├── content        # 评论内容
│   ├── likeCount      # 评论点赞数
│   └── aweme_id       # 关联视频 ID
│
├── user               # 系统登录用户表
│   ├── username
│   ├── password
│   └── createTime
│
├── system_config      # 系统配置表（AI 配置、源数据库配置等）
│   ├── config_key
│   ├── config_value
│   └── description
│
├── part1              # 评论用户 IP 地区分布（→ 地图页）
├── part2              # 点赞 / 收藏 TOP10（→ 首页图表）
├── part3              # 粉丝区间分布（→ 粉丝分析页）
├── part4              # 粉丝数量排行 TOP10（→ 粉丝分析页）
├── part5              # 评论 / 分享量 TOP10（→ 评论分析页）
└── Django 系统表       # auth_*, django_*, django_session 等
```

> `part1~part5` 为预计算统计表，页面直接读取，无需实时聚合。导入或迁移新数据后，需要刷新统计表、NLP 结果和词云图片。

## API 概览

新前端主要调用 `/api/` 下的 DRF 接口：

| 类型 | 路径 | 说明 |
|------|------|------|
| 认证 | `/api/auth/login/`、`/api/auth/register/`、`/api/auth/logout/`、`/api/auth/me/` | 登录、注册、退出、恢复当前用户 |
| 认证 | `/api/auth/change-password/` | 修改密码 |
| 数据 | `/api/dashboard/`、`/api/videos/`、`/api/comments/` | 首页统计、视频分页、评论分页 |
| 图表 | `/api/charts/ip-distribution/` | 地区分布 |
| 图表 | `/api/charts/fans-distribution/` | 粉丝区间与粉丝排行 |
| 图表 | `/api/charts/engagement/` | 评论量 / 分享量 TOP10 和高频词 |
| 图表 | `/api/charts/sentiment/` | 情感分析饼图与分值分布 |
| 图表 | `/api/charts/wordcloud/video/`、`/api/charts/wordcloud/comment/` | 词云图片 URL |
| 功能 | `/api/predict/` | 点赞预测 |
| 功能 | `/api/ai/analyze/` | AI 单视频分析 |
| 配置 | `/api/config/` | 读取 / 保存系统配置 |
| 运维 | `/api/ops/test-connection/`、`/api/ops/migrate/` | 源库连接测试与数据迁移 |
| 运维 | `/api/ops/refresh-stats/`、`/api/ops/nlp/`、`/api/ops/wordcloud/` | 刷新统计、NLP 和词云 |

## 快速部署（Docker 一键启动）

### 前置要求

- Docker >= 20.10
- Docker Compose >= 2.0

### 启动步骤

```bash
# 1. 进入项目目录
cd dy_project

# 2. （可选）配置百度千帆 API Key
#    编辑 docker-compose.yml，取消注释并填写：
#    QIANFAN_API_KEY: your_api_key
#    QIANFAN_APPID: your_appid

# 3. 一键启动并构建镜像（首次启动会自动导入 db.sql 数据）
docker compose up -d --build

# 4. 查看启动日志
docker compose logs -f web

# 5. 访问系统
#    Vue 前端：http://localhost/
#    Django Admin：http://localhost/admin/
#    后端 Admin：http://localhost:8000/admin/
#    旧模板入口：http://localhost:8000/home/login/
#    MySQL：127.0.0.1:3307
```

Compose 会启动三个服务：

- `db`：MySQL 8.0，挂载 `db.sql` 初始化业务库。
- `web`：Django 后端，启动前等待 MySQL，并执行 `migrate --run-syncdb`。
- `frontend`：Nginx 托管 Vue 构建产物，并代理 `/api/`、`/static/`、`/admin/` 到后端。

### 停止服务

```bash
docker compose down          # 停止并移除容器
docker compose down -v       # 停止并清除数据卷（会删除数据库数据）
```

## 本地开发

### 后端

```bash
# 1. 建议使用 Python 3.10+
python -m venv .venv
source .venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 MySQL 8.0 并导入 db.sql
mysql -u root -p < db.sql

# 4. 配置数据库连接（推荐使用环境变量，避免修改代码）
export DB_HOST=127.0.0.1
export DB_PORT=3306
export DB_NAME=dy_django_analysis
export DB_USER=root
export DB_PASSWORD=your_password

# 5. 运行迁移
python manage.py migrate --run-syncdb

# 6. 启动开发服务器
python manage.py runserver 0.0.0.0:8000
```

如果复用 Docker Compose 的 MySQL，数据库端口应使用宿主机映射端口：

```bash
docker compose up -d db
export DB_HOST=127.0.0.1
export DB_PORT=3307
export DB_NAME=dy_django_analysis
export DB_USER=root
export DB_PASSWORD=123456
python manage.py runserver 0.0.0.0:8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

开发访问地址：

- Vue 前端：`http://localhost:5173/`
- Django 后端：`http://127.0.0.1:8000/`

`frontend/vite.config.js` 已将 `/api` 和 `/static` 代理到 Django，因此开发时不需要手动改接口地址。

## 数据采集流程（可选）

数据已预置在 `db.sql` 中。更换数据集时有两种方式：

1. 使用 Vue 前端“数据管理”页面，从 `media_crawler` 源库迁移数据，然后依次刷新统计表、运行 NLP、生成词云。
2. 使用 `data/` 目录中的离线脚本重新采集、导入和处理数据。

如需走离线脚本流程：

```bash
cd data/

# 1. 更新 spider.py / spider_comment.py 中的 Cookie（需登录抖音后从浏览器获取）

# 2. 采集视频数据
python spider.py

# 3. 采集评论数据
python spider_comment.py

# 4. 导入数据库
python csv_to_sql.py

# 5. 生成预计算统计表（按需选择执行 part1~part5）
python data_analysis.py

# 6. NLP 情感分析（生成 nlp_result.csv）
python nlp.py

# 7. 生成词云图（生成 static/img/ 下的词云图片）
python wordCloud.py
```

如果已有 `media_crawler` 数据库，也可以在项目根目录运行：

```bash
python data/migrate_from_mediacrawler.py
```

注意：`data/nlp.py` 依赖当前工作目录读取 `stopwords.txt` 和 `comment_data.csv`，因此应在 `data/` 目录下运行；后端接口 `/api/ops/nlp/` 则使用项目绝对路径。

## 点赞预测模型

模型使用线性回归，训练特征：

| 特征 | 说明 |
|------|------|
| 视频时长 | 秒数 |
| 收藏数量 | - |
| 评论数量 | - |
| 分享数量 | - |
| 粉丝数量 | - |
| 互动率 | (点赞 + 评论 + 分享) / 粉丝数 |
| 发布小时 | 0~23 |

如需重新训练（更换数据集后）：

```bash
cd build_model/
python build.py
```

## AI 智能分析配置

`Get_Qianfan.py` 会优先从 `system_config` 表读取以下配置：

- `ai_api_key`
- `ai_base_url`
- `ai_appid`
- `ai_model`

如果数据库未配置，则回退到环境变量 `QIANFAN_API_KEY` / `QIANFAN_APPID` 和 `config.py` 中的默认值。生产环境不要依赖代码中的默认 Key，建议通过环境变量或前端“数据管理”页面配置，并轮换已经提交到仓库历史中的真实密钥。

## 安全注意事项

部署前请务必处理以下问题：

1. **API Key**：`config.py` 中含有默认 API Key，生产环境必须通过环境变量 `QIANFAN_API_KEY` / `QIANFAN_APPID` 覆盖，不要将真实 Key 提交到代码仓库
2. **数据库密码**：`docker-compose.yml` 中默认密码为 `123456`，生产环境请修改为强密码
3. **Cookie**：`data/spider.py` 中包含采集时使用的抖音 Cookie，这些 Cookie 已失效，但不应提交含有效 Cookie 的文件到公开仓库
4. **密码存储**：当前系统密码以明文存储，仅适用于本地演示/学习场景，生产环境需引入密码哈希（如 `bcrypt`）
5. **Django 配置**：当前 `DEBUG=True` 且 `ALLOWED_HOSTS` 默认放开，生产环境必须收紧
6. **敏感操作权限**：数据迁移、刷新统计、NLP、词云和 AI 配置属于写操作，应限制为管理员可用

## 已知问题与改进方向

### 安全
- [ ] 密码改为哈希存储（当前为明文）
- [ ] 轮换已经出现在仓库中的 API Key，并移除硬编码默认密钥
- [ ] 区分开发 / 生产配置，关闭生产环境 `DEBUG`，收紧 `ALLOWED_HOSTS` 和 CORS
- [ ] 为旧 `/home/` 模板路由补齐登录校验，或逐步下线旧页面，只保留 Vue + DRF 入口
- [ ] 为数据迁移、刷新统计、NLP、词云生成、AI 配置等敏感操作增加管理员权限和操作日志

### 代码质量
- [ ] `forecast.py` 的 `predict_likes()` 每次调用都从磁盘 `joblib.load` 模型文件，应在模块级别加载一次后复用
- [ ] `part3` / `part4` 旧模板视图每次请求都读取 `nlp_result.csv`，建议改为数据库查询或缓存
- [ ] `predict` 视图异常处理为 `except: return None`，会触发 HTTP 500，需返回有意义的错误响应
- [ ] `Get_Qianfan.py` 中函数名拼写错误：`analyze_single_viedo` → `analyze_single_video`
- [ ] 项目同时使用 Django ORM、原生 PyMySQL 和 SQLAlchemy，建议明确边界，避免同一类查询分散在多个数据访问方式里

### 架构
- [ ] Vue SPA 与 Django 模板页面功能重复，建议确认主入口，降低双维护成本
- [ ] `VideoData.publishTime` / `duration` 使用 `TextField` 存储，应改为对应的 `DateField` / `IntegerField`
- [ ] `VideoData.aweme_id`（TextField）与 `CommentData.aweme_id`（BigIntegerField）类型不一致，应统一
- [ ] `aweme_id`、发布时间、作者、评论归属视频等常用查询字段缺少索引
- [ ] 预计算统计表（part1~part5）与 Django 模型体系脱节；可改为 Django management command 或定时任务统一管理

### 功能扩展
- [ ] 支持自定义关键词搜索（当前数据集固定为"哪吒2"）
- [ ] 数据导出（CSV / Excel）
- [ ] 图表数据支持时间范围筛选
- [ ] 增加数据质量报告：导入去重、空值检查、异常值提示、迁移日志
- [ ] 增加模型版本、训练样本量、评估指标和预测解释
- [ ] 增加 AI 分析历史、批量分析、提示词模板和失败重试
