# Git 提交记录

> 仓库地址：`git@github.com:laycz38/Vibe_AIFriends.git`  
> 当前分支：`main`

| # | 日期时间 | 作者 | 说明 | Commit Hash |
|---|----------|------|------|-------------|
| 1 | 2026-05-18 16:45 | yuze liang | Initial commit: Django backend + Vue3 frontend with JWT auth | `871fdd3` |
| 2 | 2026-05-18 17:10 | yuze liang | 集成 Tailwind CSS + daisyUI，实现导航栏 | _待填入_ |

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
  - Git提交记录.md（本文件）
- .gitignore：忽略 `__pycache__`、`db.sqlite3`、`node_modules/`、`media/`、`static/`、`.idea/`

### #2 — 2026-05-18 17:10
**集成 Tailwind CSS + daisyUI，实现导航栏**

包含内容：
- 删除前端示例代码
  - 删除 HelloWorld.vue、TheWelcome.vue、WelcomeItem.vue
  - 删除 icons/ 目录下所有 SVG 图标组件
  - 删除 stores/counter.js（Pinia 示例）
  - 删除 assets/base.css、assets/main.css
- 安装并配置 Tailwind CSS v4
  - 安装 `tailwindcss` + `@tailwindcss/vite`
  - vite.config.js 中添加 `tailwindcss()` 插件
  - `@import "tailwindcss"` 到 main.css
- 安装并配置 daisyUI 5.5.19
  - `@plugin "daisyui"` 到 main.css
- 创建导航栏组件 `NavBar.vue`
  - 使用 daisyUI navbar 组件样式
  - 包含「首页」「关于」两个导航链接
  - AIFriends 品牌 logo 文字
- 更新 App.vue：引入 NavBar + RouterView
- 更新 HomeView.vue：简洁首页内容
- 重建 AboutView.vue：关于页面内容
- npm run build：打包到 `backend/static/frontend/`
