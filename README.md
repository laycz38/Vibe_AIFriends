# AIFriends

一个前后端分离的 Web 项目，使用 **Django 6.0 + Vue 3 + TailwindCSS + daisyUI** 构建。

> GitHub：[laycz38/Vibe_AIFriends](https://github.com/laycz38/Vibe_AIFriends)  
> 最后更新：2026-05-18

---

## 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **后端** | Django | 6.0.5 | Web 框架 |
| | Django REST Framework | 3.17.1 | REST API |
| | SimpleJWT | 5.5.1 | JWT 用户认证 |
| | django-cors-headers | 4.9.0 | 跨域请求 |
| **前端** | Vue | 3.5.32 | UI 框架 |
| | Vite | 8.0.13 | 构建 + 开发服务器 |
| | Tailwind CSS | 4.3.0 | 原子化 CSS |
| | daisyUI | 5.5.19 | Tailwind 组件库 |
| | Vue Router | 5.0.4 | 前端路由 |
| | Pinia | 3.0.4 | 状态管理 |
| **数据库** | SQLite | - | 开发环境 |

---

## 快速开始

### 环境要求

- Python（conda 环境 `vibe_AIFriends`）
- Node.js v24+

### 1. 后端

```bash
cd backend
D:\coding_software\anaconda3\envs\vibe_AIFriends\python.exe manage.py runserver
```

访问 `http://127.0.0.1:8000/`

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173/`

### 3. 管理后台

访问 `http://127.0.0.1:8000/admin/`

| 用户名 | 密码 |
|------|------|
| `admin` | `12138` |

---

## 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| Django 后端骨架 | ✅ | 项目配置、静态文件、媒体文件 |
| JWT 登录接口 | ✅ | `/api/token/` + `/api/token/refresh/` |
| CORS 跨域 | ✅ | 允许 `localhost:5173` 访问 |
| Vue 3 前端骨架 | ✅ | Vite + Router + Pinia |
| TailwindCSS + daisyUI | ✅ | 原子 CSS + UI 组件库 |
| 小红书风格首页 | ✅ | Sidebar + Header + 瀑布流 + 卡片 |
| npm → Django 打包 | ✅ | `npm run build` → `backend/static/frontend/` |
| Git 版本管理 | ✅ | GitHub: `laycz38/Vibe_AIFriends` |

---

## 项目结构

```
AIFriends/
├── README.md                    # 🏠 项目首页（本文件）
├── main.py                      # 初始 demo 脚本
├── .gitignore                   # Git 忽略规则
│
├── backend/                     # Django 后端
│   ├── manage.py                # Django 命令行入口
│   ├── db.sqlite3               # SQLite 数据库
│   ├── backend/                 # 项目配置
│   │   ├── settings.py          # CORS + JWT + 静态文件
│   │   └── urls.py              # 根路由 + 静态文件路由
│   ├── web/                     # 业务应用
│   │   ├── urls.py              # JWT token 接口
│   │   ├── models.py
│   │   └── views.py
│   └── static/frontend/         # npm run build 输出
│
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── App.vue              # 根组件
│   │   ├── main.js              # 入口
│   │   ├── assets/main.css      # Tailwind + daisyUI
│   │   ├── data/notes.js        # 15 条 mock 笔记数据
│   │   ├── components/
│   │   │   ├── Sidebar.vue      # 左侧固定侧边栏（280px）
│   │   │   ├── Header.vue       # 顶部固定 Header（72px）
│   │   │   ├── FeedWaterfall.vue# 瀑布流布局
│   │   │   ├── NoteCard.vue     # 笔记卡片
│   │   │   └── NavBar.vue       # daisyUI 导航栏（备用）
│   │   ├── views/
│   │   │   ├── HomeView.vue
│   │   │   └── AboutView.vue
│   │   └── router/index.js      # 路由配置
│   ├── vite.config.js           # Tailwind 插件 + 打包路径
│   └── package.json             # npm 依赖
│
└── 项目文档/                     # 📁 项目参考文档
    ├── 项目架构文档.md            # 技术架构详解
    ├── 学习笔记.md                # JWT 认证学习笔记
    ├── AI提示词文档.md            # AI 提示词记录 & 模板
    └── Git提交记录.md             # Git 提交历史
```

---

## API 接口

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/admin/` | Session | Django 管理后台 |
| POST | `/api/token/` | 无 | 登录获取 JWT token |
| POST | `/api/token/refresh/` | 无 | 刷新 access token |
| GET | `/assets/*` | 无 | 前端打包静态资源（仅 DEBUG） |
| GET | `/media/*` | 无 | 用户上传文件（仅 DEBUG） |

---

## 常用命令

### 后端

```bash
cd backend
python manage.py runserver          # 启动
python manage.py makemigrations     # 创建迁移
python manage.py migrate            # 执行迁移
python manage.py check              # 系统检查
```

### 前端

```bash
cd frontend
npm run dev          # 启动开发服务器
npm run build        # 打包到 Django static
```

---

## 参考文档

| 文档 | 路径 |
|------|------|
| 技术架构详解 | [项目文档/项目架构文档.md](项目文档/项目架构文档.md) |
| JWT 认证学习笔记 | [项目文档/学习笔记.md](项目文档/学习笔记.md) |
| AI 提示词记录 | [项目文档/AI提示词文档.md](项目文档/AI提示词文档.md) |
| Git 提交历史 | [项目文档/Git提交记录.md](项目文档/Git提交记录.md) |
