# Git 提交记录

> 仓库地址：`git@github.com:laycz38/Vibe_AIFriends.git`  
> 当前分支：`main`

| # | 日期时间 | 作者 | 说明 | Commit Hash |
|---|----------|------|------|-------------|
| 1 | 2026-05-18 16:45 | yuze liang | Initial commit: Django backend + Vue3 frontend with JWT auth | `871fdd3` |
| 2 | 2026-05-18 17:10 | yuze liang | 集成 Tailwind CSS + daisyUI，实现导航栏 | `a12bd6c` |
| 3 | 2026-05-18 17:15 | yuze liang | 小红书风格首页布局 + 文档整理 | _待填入_ |

### #1 — 2026-05-18 16:45
**Initial commit: Django backend + Vue3 frontend with JWT auth**

包含内容：
- Django 后端项目骨架（`backend/`）
  - settings.py：CORS、JWT、SimpleJWT、静态文件、时区等配置
  - urls.py：管理后台 + JWT 接口 + 静态文件路由
  - web 应用：token 获取与刷新接口
- Vue 3 前端项目骨架（`frontend/`）
  - Vue Router + Pinia
  - vite.config.js：打包输出到 `backend/static/frontend/`
- 项目文档
  - 项目架构文档.md
  - 学习笔记.md（JWT 认证详解）
  - README.md
  - Git提交记录.md
- .gitignore：忽略 `__pycache__`、`db.sqlite3`、`node_modules/`、`media/`、`static/`、`.idea/`

### #2 — 2026-05-18 17:10
**集成 Tailwind CSS + daisyUI，实现导航栏**

包含内容：
- 删除前端示例代码（HelloWorld、icons、counter.js 等 12 个文件）
- 安装 Tailwind CSS v4 + @tailwindcss/vite + daisyUI 5.5.19
- vite.config.js 添加 tailwindcss 插件
- main.css 配置 @import tailwindcss + @plugin daisyui
- 创建 NavBar 导航栏组件（daisyUI navbar）
- 更新 App.vue / HomeView / AboutView

### #3 — 2026-05-18 17:15
**小红书风格首页布局 + 文档整理**

包含内容：
- 创建 `src/data/notes.js`：15 条 mock 笔记数据 + 分类 + 菜单
- 创建 `Sidebar.vue`：左侧固定侧边栏（280px）
  - Logo、菜单项（发现/直播/发布/通知）
  - 登录按钮、登录提示卡片、更多
- 创建 `Header.vue`：顶部固定 Header（72px）
  - 搜索框（圆角、浅灰背景、placeholder）
  - 11 个分类 Tab（推荐/穿搭/美食/彩妆/影视/职场/情感/家居/游戏/旅行/健身）
  - 创作中心 + 业务合作
- 创建 `FeedWaterfall.vue`：瀑布流容器（CSS columns，响应式 2-5 列）
- 创建 `NoteCard.vue`：笔记卡片
  - 图片 + 标题（两行省略）+ 作者头像/名称 + 爱心/点赞数
  - hover 上浮 + 图片放大动画
- 更新 `App.vue`：整合 Sidebar + Header + FeedWaterfall
- 新增 `main.css` scrollbar-hide utility
- 文档整理：所有 `.md` 参考文档移入 `项目文档/` 文件夹
  - 新增 `AI提示词文档.md`
  - README.md 更新项目结构
