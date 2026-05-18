# AI 提示词文档

> 用途：记录项目中使用的 AI 生成提示词，方便后续复现和调整  
> 创建日期：2026-05-18  
> 最后更新：2026-05-18

---

## 使用说明

本文档记录了 AIFriends 项目从零到现阶段的每个关键步骤所使用的提示词。每条提示词包含：
- **场景**：在什么上下文使用
- **输入**：给 AI 的指令
- **产出**：AI 生成/修改的文件列表
- **状态**：完成情况

新开对话时，按需复制对应提示词，粘贴即可复现。

---

## 提示词一：Django 后端项目初始化

### 使用场景
在已有 conda 虚拟环境、已安装 Django 依赖的前提下，创建 Django 项目骨架。

### 用户输入
```
在AIFriends/目录下执行：
django-admin startproject backend
cd backend
django-admin startapp web
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### 产出
| 文件 | 说明 |
|------|------|
| `backend/manage.py` | Django 命令行入口 |
| `backend/backend/settings.py` | 项目配置 |
| `backend/backend/urls.py` | 根路由 |
| `backend/backend/wsgi.py` / `asgi.py` | 部署入口 |
| `backend/web/` | web 应用 |
| `backend/db.sqlite3` | 数据库 |

### 状态
✅ 完成

---

## 提示词二：Django 配置 CORS + JWT + 静态文件

### 使用场景
后端项目已创建，需要配置跨域、JWT 认证、静态/媒体文件路由。

### 用户输入
```
在AIFriends/backend/backend/settings.py中：
注册 app：rest_framework、web、corsheaders
加入跨域中间件 CorsMiddleware（尽量靠前）
设置时区 Asia/Shanghai
设置 STATICFILES_DIRS、MEDIA_URL、MEDIA_ROOT
配置 REST_FRAMEWORK JWT 认证
配置 SIMPLE_JWT（access 2h, refresh 7d, rotate, blacklist）

在 web/urls.py 中配置 JWT 接口：
/api/token/ → TokenObtainPairView
/api/token/refresh/ → TokenRefreshView

在 backend/urls.py 中：
include web.urls
DEBUG 时添加 /assets/ 和 /media/ 静态路由
```

### 产出
| 文件 | 说明 |
|------|------|
| `backend/backend/settings.py` | INSTALLED_APPS、MIDDLEWARE、TIME_ZONE、STATIC/MEDIA、CORS、REST_FRAMEWORK、SIMPLE_JWT |
| `backend/backend/urls.py` | 根路由 + DEBUG 静态路由 |
| `backend/web/urls.py` | JWT token + refresh 接口 |
| `backend/static/` | 静态文件目录 |
| `backend/media/` | 媒体文件目录 |

### 状态
✅ 完成

---

## 提示词三：Vue 3 前端项目创建

### 使用场景
需要创建 Vue 3 前端项目，使用 Vite 构建，集成 Router 和 Pinia。

### 用户输入
```
在AIFriends/目录下执行：
npm create vue@latest
项目名称：frontend
包含功能：Router、Pinia

cd frontend
npm install
npm run dev

在 vite.config.js 中配置打包输出路径：
build.outDir = path.resolve(__dirname, '../backend/static/frontend')
```

### 产出
| 文件 | 说明 |
|------|------|
| `frontend/` | Vue 3 项目完整目录 |
| `frontend/vite.config.js` | 添加 build.outDir |
| `frontend/src/router/index.js` | 路由配置 |
| `frontend/src/stores/counter.js` | Pinia 示例 |

### 状态
✅ 完成

---

## 提示词四：集成 Tailwind CSS + daisyUI，实现导航栏

### 使用场景
前端项目已创建，需要引入 CSS 框架并实现导航栏。

### 用户输入
```
安装 tailwindcss @tailwindcss/vite daisyui
在 vite.config.js 添加 tailwindcss() 插件
在 main.css 配置 @import "tailwindcss" + @plugin "daisyui"
删除前端示例代码（HelloWorld、icons、counter store 等）
创建 NavBar.vue 导航栏（daisyUI navbar 组件）
更新 App.vue、HomeView、AboutView
npm run build
```

### 产出
| 文件 | 说明 |
|------|------|
| `vite.config.js` | 添加 tailwindcss 插件 |
| `src/assets/main.css` | Tailwind + daisyUI 入口 |
| `src/components/NavBar.vue` | 导航栏组件 |
| `src/App.vue` | NavBar + RouterView |
| `src/views/HomeView.vue` | 首页 |
| `src/views/AboutView.vue` | 关于页 |
| 删除 12 个示例文件 | HelloWorld、icons、counter.js 等 |

### 状态
✅ 完成

---

## 提示词五：小红书风格首页布局（核心）

### 使用场景
已有完整的 Vue3 + Vite + TailwindCSS4 + daisyUI 前端项目，需要高还原度的小红书 Web 首页。

### 完整提示词

```
使用 Vue3 + Vite + TailwindCSS4 + daisyUI 实现一个"小红书风格"的首页布局，要求高还原度。

技术要求：
- Vue3 Composition API（<script setup>）
- TailwindCSS 4
- 可使用 daisyUI
- 页面需响应式
- 组件化开发
- 不要使用 Element Plus
- 风格简洁，接近小红书 Web 首页

页面整体布局：左侧固定 Sidebar（280px）+ 顶部固定 Header（72px）+ 中间瀑布流 Masonry

页面结构：
App → Sidebar + Header + FeedWaterfall → NoteCard

Sidebar：Logo、菜单（发现/直播/发布/通知）、登录按钮、提示卡片、更多
Header：居中搜索框 ~600px、分类Tab 11项（推荐/穿搭/美食等）、创作中心/业务合作
FeedWaterfall：CSS columns 瀑布流，响应式 2-5 列
NoteCard：图片（比例不固定）、标题（两行省略）、作者头像+名称、爱心+点赞数

UI 风格：
- 主色 #ff2442、背景 #f7f7f7
- 圆角 rounded-2xl、shadow-sm → hover:shadow-lg
- hover 上浮 -translate-y-1 + 图片放大 scale-105
- 禁止过重边框、花哨渐变，极简高级留白

数据：15 条 mock 笔记，含图片/标题/作者/点赞数，v-for 渲染
```

### 产出
| 文件 | 说明 |
|------|------|
| `src/data/notes.js` | 15 条 mock 数据 + 分类 + 菜单 |
| `src/components/Sidebar.vue` | 左侧固定侧边栏（280px） |
| `src/components/Header.vue` | 顶部固定 Header + 分类 Tab |
| `src/components/FeedWaterfall.vue` | CSS columns 瀑布流容器 |
| `src/components/NoteCard.vue` | 笔记卡片（hover 动画） |
| `src/App.vue` | 整合所有组件 |
| `src/assets/main.css` | 添加 scrollbar-hide utility |

### 状态
✅ 完成

---

## 提示词六：项目文档整理

### 使用场景
项目功能开发告一段落，需要整理参考文档。

### 用户输入
```
帮我写一个AI提示词文档，记录目前使用的提示词
把所有参考文档（.md）都放到一个文件夹中
名字叫 项目文档
```

### 产出
| 文件 | 说明 |
|------|------|
| `项目文档/` 文件夹 | 集中存放所有参考文档 |
| `项目文档/AI提示词文档.md` | 新建 |
| `项目文档/Git提交记录.md` | 移入 |
| `项目文档/学习笔记.md` | 移入 |
| `项目文档/项目架构文档.md` | 移入 |

### 状态
✅ 完成

---

## 提示词七：Git 仓库初始化与推送

### 使用场景
需要创建 Git 仓库并推送到 GitHub。

### 用户输入
```
创建 .gitignore（忽略 __pycache__、db.sqlite3、node_modules/、media/、static/、.idea/）
创建 README.md
git init → git add → git commit
git remote add origin git@github.com:laycz38/Vibe_AIFriends.git
git branch -M main → git push -u origin main
```

### 产出
| 文件 | 说明 |
|------|------|
| `.gitignore` | Git 忽略规则 |
| `README.md` | GitHub 首页 |
| GitHub 仓库 | `laycz38/Vibe_AIFriends` |

### 状态
✅ 完成

---

## 提示词模板：前端新页面 / 新功能

```
使用 Vue3 + Vite + TailwindCSS4 + daisyUI 实现一个 [功能描述] 页面/组件。

技术要求：
- Vue3 Composition API（<script setup>）
- TailwindCSS 4 原子类
- 可用 daisyUI 组件
- 响应式设计
- 组件化拆分

页面结构：
[描述布局和组件树]

数据：
[描述 mock 数据格式和数量]

UI 风格：
- 主色 #ff2442
- 背景 #f7f7f7
- 卡片 rounded-2xl shadow-sm hover:shadow-lg
- 文字 gray-900/700/500/400
- [其他风格要求]
```

---

## 提示词模板：Django 后端 API

```
在现有 Django + DRF + SimpleJWT 项目中，实现 [功能描述]。

技术要求：
- Django REST Framework
- JWT 认证
- [其他要求]

数据模型（Model）：
[描述字段]

API 接口：
| 方法 | 路径 | 认证 | 说明 |
[接口列表]

要求：
- Serializer 序列化器
- ViewSet 或 APIView
- 路由注册
```

---

## 提示词模板：更新项目文档

```
根据目前整个项目的制作流程和聊天内容，更新下面三个文档：
1. README.md
2. AI提示词文档.md
3. 项目架构文档.md

要求：全面反映项目当前真实状态，包括所有文件、技术栈、功能清单。
```

---

## 提示词使用记录

| # | 日期 | 提示词 | 状态 | 说明 |
|---|------|--------|------|------|
| 1 | 2026-05-18 | Django 后端初始化 | ✅ | 创建项目 + 迁移 + 超级管理员 |
| 2 | 2026-05-18 | Django CORS + JWT 配置 | ✅ | settings.py + urls.py 完整配置 |
| 3 | 2026-05-18 | Vue 3 前端创建 | ✅ | Vite + Router + Pinia + 打包配置 |
| 4 | 2026-05-18 | Tailwind + daisyUI + NavBar | ✅ | CSS 框架 + 导航栏 + 清理示例代码 |
| 5 | 2026-05-18 | 小红书首页布局 | ✅ | Sidebar + Header + 瀑布流 + 15 条卡片 |
| 6 | 2026-05-18 | 项目文档整理 | ✅ | 文件夹 + AI提示词文档 |
| 7 | 2026-05-18 | Git 仓库初始化 | ✅ | .gitignore + README + push |
| 8 | 2026-05-18 | 全部文档更新 | ✅ | README + 架构文档 + 提示词文档 |

---

> 💡 **使用方式**：新开对话时，复制对应提示词，粘贴即可复现相同效果。根据实际需求微调参数和数据。
