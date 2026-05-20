# AIFriends

> 🎯 AI 面经社区平台 — 前后端分离的 Web 项目，小红书风格布局，支持用户发布面经、点赞评论、AI 智能检索。  
> 使用 **Django 6.0 + Vue 3 + TailwindCSS + daisyUI** 构建。

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
| JWT 登录接口 | ✅ | `access_token`（2h）+ `refresh_token`（7d） |
| 用户注册 | ✅ | 创建账号 + 自动返回 token |
| 用户登录 | ✅ | 用户名+密码 → JWT + cookie |
| 用户退出 | ✅ | 清除 cookie 中 refresh_token |
| Token 刷新 | ✅ | 401 自动刷新，队列机制防并发 |
| CORS 跨域 | ✅ | 允许 `localhost:5173` 访问 |
| Vue 3 前端骨架 | ✅ | Vite + Router + Pinia |
| TailwindCSS + daisyUI | ✅ | 原子 CSS + UI 组件库 |
| 前端路由系统 | ✅ | 10 个页面 + 动态路由 + 404 |
| 路由守卫 | ✅ | 未登录自动跳转登录页（带 redirect） |
| 全局状态管理 | ✅ | Pinia user store + localStorage 持久化 |
| axios HTTP 封装 | ✅ | 自动带 token + 401 自动刷新 |
| 首屏拉取用户信息 | ✅ | App.vue onMounted 拉取 |
| 小红书风格首页 | ✅ | Sidebar + Header + 瀑布流 + 真实数据 |
| 面经发布 | ✅ | 标题/内容/公司/岗位/难度/封面上传 |
| 本地图片上传 | ✅ | ImageField + FormData 上传封面/头像 |
| 面经详情页 | ✅ | 点击卡片进入 + 阅读布局 |
| 面经点赞 | ✅ | 登录后点赞/取消点赞 |
| 面经评论 | ✅ | 登录后发表评论 |
| 用户头像 | ✅ | 来自数据库，右上角显示 |
| 用户简介 | ✅ | 个人资料页编辑 |
| 用户空间 | ✅ | 动态路由 `/user/:user_id/` |
| 左侧栏伸缩布局 | 🔧 | 点击按钮展开/收起侧栏 |
| npm → Django 打包 | ✅ | `npm run build` → `backend/static/frontend/` |
| Django 托管前端 | ✅ | 任意路径刷新回退 `index.html` |
| 生产环境同源修复 | ✅ | 打包后 api 使用相对路径 |
| Git 版本管理 | ✅ | GitHub: `laycz38/Vibe_AIFriends` |

---

## 项目结构

```
AIFriends/
├── README.md                    # 🏠 项目首页（本文件）
├── .gitignore                   # Git 忽略规则
│
├── backend/                     # Django 后端
│   ├── manage.py                # Django 命令行入口
│   ├── db.sqlite3               # SQLite 数据库
│   ├── media/                   # 用户上传文件（头像/封面）
│   ├── backend/                 # 项目配置
│   │   ├── settings.py          # CORS + JWT + 静态文件
│   │   └── urls.py              # 根路由 + 静态文件路由
│   ├── web/                     # 业务应用
│   │   ├── admin.py             # 后台模型注册
│   │   ├── models.py            # 数据模型（4个：UserProfile/Note/Like/Comment）
│   │   ├── urls.py              # 全部 API 路由（14个接口）
│   │   ├── views/               # 视图（按模块拆分）
│   │   │   ├── index.py         # 前端回退视图
│   │   │   ├── note/            # 面经相关视图
│   │   │   │   ├── create.py    # 发布面经
│   │   │   │   ├── get_list.py  # 面经列表
│   │   │   │   ├── get_detail.py# 面经详情
│   │   │   │   ├── toggle_like.py    # 点赞/取消
│   │   │   │   ├── create_comment.py # 发表评论
│   │   │   │   └── common.py   # 序列化工具
│   │   │   └── user/account/    # 用户认证视图
│   │   │       ├── login.py     # 登录
│   │   │       ├── register.py  # 注册
│   │   │       ├── logout.py    # 退出
│   │   │       ├── refresh_token.py  # 刷新 token
│   │   │       ├── get_user_info.py  # 获取用户信息
│   │   │       ├── update_profile.py # 更新资料
│   │   │       └── common.py   # 序列化工具
│   │   └── migrations/          # 数据库迁移（5个）
│   └── static/frontend/         # npm run build 输出
│
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── App.vue              # 根组件（Sidebar + Header + RouterView）
│   │   ├── main.js              # 入口（Pinia + Router）
│   │   ├── assets/main.css      # Tailwind + daisyUI
│   │   ├── data/notes.js        # 分类 + 菜单 + mock 数据
│   │   ├── stores/
│   │   │   └── user.js          # Pinia 用户状态管理
│   │   ├── js/http/
│   │   │   └── api.js           # axios 封装 + 拦截器
│   │   ├── components/
│   │   │   ├── Sidebar.vue      # 左侧侧边栏
│   │   │   ├── Header.vue       # 顶部 Header
│   │   │   ├── FeedWaterfall.vue# 瀑布流布局
│   │   │   ├── NoteCard.vue     # 面经卡片
│   │   │   └── navbar/
│   │   │       └── UserMenu.vue # 用户头像下拉菜单
│   │   ├── views/
│   │   │   ├── homepage/HomepageIndex.vue  # 首页
│   │   │   ├── create/CreateIndex.vue      # 发布面经
│   │   │   ├── note/NoteDetailIndex.vue    # 面经详情
│   │   │   ├── friend/FriendIndex.vue      # AI 模拟面试
│   │   │   ├── profile/ProfileIndex.vue    # 个人资料编辑
│   │   │   ├── user/account/LoginIndex.vue # 登录
│   │   │   ├── user/account/RegisterIndex.vue # 注册
│   │   │   ├── user/space/SpaceIndex.vue   # 用户空间
│   │   │   └── error/NotFoundIndex.vue     # 404
│   │   └── router/index.js      # 路由配置 + 守卫
│   ├── vite.config.js           # Tailwind 插件 + 打包路径 + 固定端口
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

### 认证相关
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/user/account/login/` | 无 | 登录（返回 access_token + set refresh cookie） |
| POST | `/api/user/account/register/` | 无 | 注册 |
| POST | `/api/user/account/logout/` | JWT | 退出（清除 refresh cookie） |
| POST | `/api/user/account/refresh_token/` | Cookie | 刷新 access_token |
| GET | `/api/user/account/info/` | JWT | 获取用户信息 |
| POST | `/api/user/account/update_profile/` | JWT | 更新头像/简介 |

### 面经相关
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/notes/` | 无 | 首页面经列表 |
| POST | `/api/notes/create/` | JWT | 发布面经（支持封面 FormData） |
| GET | `/api/notes/<note_id>/` | 无 | 面经详情 |
| POST | `/api/notes/<note_id>/toggle_like/` | JWT | 点赞/取消点赞 |
| POST | `/api/notes/<note_id>/comments/create/` | JWT | 发表评论 |

### 其他
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/token/` | JWT 获取 token（原始 SimpleJWT） |
| POST | `/api/token/refresh/` | JWT 刷新 token（原始 SimpleJWT） |
| GET | `/admin/` | Django 管理后台 |

---

## 数据模型

| 模型 | 字段 | 说明 |
|------|------|------|
| **UserProfile** | user(1:1), photo, bio | 用户资料扩展 |
| **InterviewNote** | user(FK), title, content, cover, company, position, difficulty, likes | 面经笔记 |
| **InterviewNoteLike** | user(FK), note(FK) + unique | 点赞记录 |
| **InterviewNoteComment** | user(FK), note(FK), content | 评论 |

---

## 常用命令

### 后端

```bash
cd backend
python manage.py runserver          # 启动
python manage.py makemigrations     # 创建迁移
python manage.py migrate            # 执行迁移
python manage.py check              # 系统检查
python manage.py createsuperuser    # 创建管理员
```

### 前端

```bash
cd frontend
npm run dev          # 启动开发服务器（固定 :5173）
npm run build        # 打包到 Django static
```

### 生产部署（Django 托管前端）

```bash
cd frontend && npm run build   # 打包前端
cd ../backend && python manage.py runserver  # Django 同时提供前后端
```

访问 `http://localhost:8000/`，前端任意路径刷新均由 Django 兜底。

---

## 参考文档

| 文档 | 路径 |
|------|------|
| 技术架构详解 | [项目文档/项目架构文档.md](项目文档/项目架构文档.md) |
| JWT 认证学习笔记 | [项目文档/学习笔记.md](项目文档/学习笔记.md) |
| AI 提示词记录 | [项目文档/AI提示词文档.md](项目文档/AI提示词文档.md) |
| Git 提交历史 | [项目文档/Git提交记录.md](项目文档/Git提交记录.md) |
