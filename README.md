# AIFriends

> 🎯 AI 面经社区平台 — 前后端分离的 Web 项目，daisyUI 风格布局，支持用户发布面经、点赞评论、搜索和 AI 智能检索。  
> 使用 **Django 6.0 + Vue 3 + TailwindCSS v4 + daisyUI v5** 构建。

> GitHub：[laycz38/Vibe_AIFriends](https://github.com/laycz38/Vibe_AIFriends)  
> 最后更新：2026-05-20

---

## 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **后端** | Django | 6.0.5 | Web 框架 |
| | Django REST Framework | 3.17.1 | REST API |
| | SimpleJWT | 5.5.1 | JWT 用户认证 |
| | django-cors-headers | 4.9.0 | 跨域请求 |
| | Pillow | - | 图片处理（头像/封面上传） |
| **前端** | Vue | 3.5.32 | UI 框架 |
| | Vite | 8.0.13 | 构建 + 开发服务器 |
| | Tailwind CSS | 4.3.0 | 原子化 CSS |
| | daisyUI | 5.5.19 | Tailwind 组件库 |
| | Vue Router | 5.0.4 | 前端路由 |
| | Pinia | 3.0.4 | 状态管理 |
| | axios | 1.16.1 | HTTP 请求 |
| **数据库** | SQLite | - | 开发环境 |

---

## 快速开始

### 环境要求

- Python（conda 环境 `vibe_AIFriends`）
- Node.js v24+

### 1. 后端

```bash
cd backend

# 首次运行需要安装 Pillow
D:\coding_software\anaconda3\envs\vibe_AIFriends\python.exe -m pip install Pillow

# 数据库迁移
D:\coding_software\anaconda3\envs\vibe_AIFriends\python.exe manage.py migrate

# 启动开发服务器
D:\coding_software\anaconda3\envs\vibe_AIFriends\python.exe manage.py runserver
```

访问 `http://127.0.0.1:8000/`

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173/`（已固定端口）

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
| JWT 登录/注册/退出 | ✅ | `access_token`（2h）+ `refresh_token`（7d） |
| Token 自动刷新 | ✅ | axios 拦截器 + 队列防并发 |
| CORS 跨域 | ✅ | 开发环境 `localhost:5173` |
| Vue 3 + daisyUI 前端 | ✅ | Router + Pinia + axios + Tailwind v4 |
| daisyUI 响应式布局 | ✅ | drawer 侧栏 + navbar 顶栏（`lg:drawer-open`） |
| 首页 Grid 自适应网格 | ✅ | `grid-cols-[repeat(auto-fill,minmax(240px,1fr))]` |
| 面经发布 | ✅ | 标题/内容/公司/岗位/难度/FormData 封面上传 |
| 默认封面图片 | ✅ | `picsum.photos/seed/tech_office` 现代办公场景 |
| 面经详情 | ✅ | daisyUI `card` + `chat` 评论气泡 |
| 面经点赞/评论 | ✅ | toggle 模式 + 唯一约束 |
| 面经搜索 | ✅ | `?q=` 参数，后端 Q 多字段 `icontains` 过滤 |
| 用户头像 + 下拉菜单 | ✅ | daisyUI `dropdown` + `avatar` |
| 个人资料编辑 | ✅ | 头像裁剪 + 简介 |
| 10 个前端页面 | ✅ | 含动态路由 `/user/:id/` `/notes/:id/` |
| 路由守卫 | ✅ | 未登录跳转 + redirect |
| Django 托管前端 | ✅ | SPA fallback `re_path` |
| npm → Django 打包 | ✅ | `npm run build` → `backend/static/frontend/` |
| Git 版本管理 | ✅ | GitHub: `laycz38/Vibe_AIFriends` |

---

## 项目结构

```
AIFriends/
├── README.md                    # 🏠 项目首页
├── .gitignore
│
├── backend/                     # Django 后端
│   ├── manage.py
│   ├── db.sqlite3
│   ├── media/                   # 用户上传（头像/封面）
│   ├── backend/
│   │   ├── settings.py          # CORS + JWT + 模板
│   │   └── urls.py              # 根路由
│   ├── web/
│   │   ├── admin.py             # 4个模型后台注册
│   │   ├── models.py            # UserProfile / InterviewNote / Like / Comment
│   │   ├── urls.py              # 14个 API 路由
│   │   ├── views/
│   │   │   ├── index.py         # SPA fallback
│   │   │   ├── note/            # get_list / get_detail / create / toggle_like / create_comment
│   │   │   └── user/account/    # login / register / logout / refresh / info / update_profile
│   │   └── migrations/          # 5个迁移
│   └── static/frontend/         # npm run build 输出
│
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── App.vue              # NavBar 包裹 RouterView
│   │   ├── main.js
│   │   ├── assets/main.css      # @import tailwindcss + @plugin daisyui
│   │   ├── data/notes.js        # 分类 + 菜单配置
│   │   ├── stores/user.js       # Pinia 用户状态
│   │   ├── js/http/api.js       # axios + 401 自动刷新
│   │   ├── components/
│   │   │   ├── navbar/
│   │   │   │   ├── NavBar.vue   # daisyUI drawer + navbar
│   │   │   │   ├── UserMenu.vue # 用户下拉菜单
│   │   │   │   └── icons/       # 6个 SVG 图标组件
│   │   │   ├── FeedWaterfall.vue# Grid 自适应网格
│   │   │   ├── NoteCard.vue     # 面经卡片（240px / hover scale-120）
│   │   │   ├── Sidebar.vue      # （旧版，已停用）
│   │   │   └── Header.vue       # （旧版，已停用）
│   │   ├── views/
│   │   │   ├── homepage/HomepageIndex.vue
│   │   │   ├── note/NoteDetailIndex.vue  # daisyUI card + chat 评论
│   │   │   ├── create/CreateIndex.vue
│   │   │   ├── friend/FriendIndex.vue
│   │   │   ├── profile/ProfileIndex.vue
│   │   │   ├── user/account/{Login,Register}Index.vue
│   │   │   ├── user/space/SpaceIndex.vue
│   │   │   └── error/NotFoundIndex.vue
│   │   └── router/index.js      # 10个路由 + 守卫
│   ├── vite.config.js           # 固定端口 5173 + 打包路径
│   └── package.json
│
└── 项目文档/
    ├── 项目架构文档.md
    ├── 学习笔记.md
    ├── AI提示词文档.md
    └── Git提交记录.md
```

---

## API 接口

### 认证
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/user/account/login/` | 无 | 登录（JWT + refresh cookie） |
| POST | `/api/user/account/register/` | 无 | 注册 |
| POST | `/api/user/account/logout/` | JWT | 退出 |
| POST | `/api/user/account/refresh_token/` | Cookie | 刷新 access_token |
| GET | `/api/user/account/info/` | JWT | 用户信息 |
| POST | `/api/user/account/update_profile/` | JWT | 更新头像/简介 |

### 面经
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/notes/` | 无 | 面经列表（支持 `?search_query=` 搜索） |
| POST | `/api/notes/create/` | JWT | 发布面经（FormData 传封面） |
| GET | `/api/notes/<id>/` | 无 | 面经详情 |
| POST | `/api/notes/<id>/toggle_like/` | JWT | 点赞/取消 |
| POST | `/api/notes/<id>/comments/create/` | JWT | 发表评论 |

---

## 数据模型

| 模型 | 关系 | 字段 |
|------|------|------|
| **UserProfile** | 1:1 User | photo, bio |
| **InterviewNote** | FK User | title, content, cover, company, position, difficulty, likes |
| **InterviewNoteLike** | FK User + FK Note | unique(user, note) |
| **InterviewNoteComment** | FK User + FK Note | content |

---

## 常用命令

```bash
# 后端
cd backend
python manage.py runserver

# 前端（HMR 热更新）
cd frontend
npm run dev          # → localhost:5173

# 生产预览
cd frontend && npm run build
cd ../backend && python manage.py runserver  # → localhost:8000
```

---

## 参考文档

| 文档 | 路径 |
|------|------|
| 技术架构 | [项目文档/项目架构文档.md](项目文档/项目架构文档.md) |
| JWT 学习笔记 | [项目文档/学习笔记.md](项目文档/学习笔记.md) |
| AI 提示词 | [项目文档/AI提示词文档.md](项目文档/AI提示词文档.md) |
| Git 历史 | [项目文档/Git提交记录.md](项目文档/Git提交记录.md) |
