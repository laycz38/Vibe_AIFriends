# AIFriends

> 🎯 AI 面经社区平台 — 前后端分离的 Web 项目，daisyUI 风格布局，支持用户发布面经、点赞评论、搜索和 AI 智能检索。  
> 使用 **Django 6.0 + Vue 3 + TailwindCSS v4 + daisyUI v5** 构建。  
> 已部署：**[app6809.acapp.acwing.com.cn](https://app6809.acapp.acwing.com.cn)**（Ubuntu 24.04 + Nginx + Gunicorn）

> GitHub：[laycz38/Vibe_AIFriends](https://github.com/laycz38/Vibe_AIFriends)  
> 最后更新：2026-05-22

---

## 技术栈

| 层级 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **后端** | Django | 6.0.5 | Web 框架 |
| | Django REST Framework | 3.17.1 | REST API |
| | SimpleJWT | 5.5.1 | JWT 用户认证 |
| | django-cors-headers | 4.9.0 | 跨域请求 |
| | Gunicorn | 23.x | 生产 WSGI 服务器 |
| | Pillow | - | 图片处理（Base64 压缩/转码） |
| **AI** | DeepSeek API | - | 智能对话 + 模拟面试 |
| | 阿里云百炼 CosyVoice | dashscope SDK 1.25 | WebSocket 流式语音合成（longanhuan / longanyang） |
| **前端** | Vue | 3.5.32 | UI 框架 |
| | Vite | 8.0.13 | 构建 + 开发服务器 |
| | Tailwind CSS | 4.3.0 | 原子化 CSS |
| | daisyUI | 5.5.19 | Tailwind 组件库 |
| | Vue Router | 5.0.4 | 前端路由 |
| | Pinia | 3.0.4 | 状态管理 |
| | axios | 1.16.1 | HTTP 请求 |
| **数据库** | SQLite | - | 开发/生产环境 |
| **部署** | Nginx | - | 反向代理 + 静态文件 + SSL |

---

## 快速开始

### 环境要求

- Python（conda 环境 `vibe_AIFriends`）
- Node.js v24+

### 1. 后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 启动开发服务器
python manage.py runserver
```

访问 `http://127.0.0.1:8000/`

### 2. 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173/`（已固定端口）

### 3. 生产部署

```bash
cd frontend && npm run build         # 构建前端
cd ../backend                         # 生产用 Gunicorn + Nginx
```

详见 [项目文档/CLAUDE_DEPLOY.md](项目文档/CLAUDE_DEPLOY.md)

---

## 已上线地址

| 环境 | 地址 |
|------|------|
| 生产 | **[app6809.acapp.acwing.com.cn](https://app6809.acapp.acwing.com.cn)** |
| 服务器 | `121.43.36.186` (Ubuntu 24.04) |
| 本地开发 | `http://localhost:5173/` (Vite) |

---

## 已实现功能

| 功能 | 状态 | 说明 |
|------|------|------|
| Django 后端骨架 | ✅ | 项目配置、路由、5个数据模型、阿里云 TTS 集成 |
| JWT 登录/注册/退出 | ✅ | `access_token`（2h）+ `refresh_token`（7d） |
| Token 自动刷新 | ✅ | axios 拦截器 + 队列防并发 |
| daisyUI 响应式布局 | ✅ | drawer 侧栏 + navbar 顶栏（`lg:drawer-open`） |
| 首页 Grid 自适应网格 | ✅ | `grid-cols-[repeat(auto-fill,minmax(240px,1fr))]` |
| 面经发布 | ✅ | 标题/内容/公司/岗位/难度 + Base64 封面上传 |
| 图片 Base64 数据库存储 | ✅ | ImageField → TextField，自动压缩至 1200px |
| 默认封面图片 | ✅ | `picsum.photos/seed/tech_office` |
| 面经详情 | ✅ | daisyUI `card` + `chat` 评论气泡 |
| 面经点赞/评论 | ✅ | toggle 模式 + 唯一约束 |
| 面经收藏 | ✅ | toggle 模式 + 独立收藏列表页 `/favorites/` |
| 面经搜索 | ✅ | `?q=` 参数，后端 Q 多字段 `icontains` 过滤 |
| 用户头像 + 下拉菜单 | ✅ | daisyUI `dropdown` + `avatar` |
| 个人资料编辑 | ✅ | Base64 头像上传 + 简介 |
| 路由守卫 | ✅ | 未登录跳转 + redirect |
| Django 托管前端 | ✅ | SPA fallback `re_path` |
| 生产环境变量配置 | ✅ | `settings.py` 读取 `DJANGO_DEBUG` / `DJANGO_SECRET_KEY` |
| Nginx + Gunicorn 部署 | ✅ | `app6809.acapp.acwing.com.cn` |
| 一键部署脚本 | ✅ | `deploy.py`（构建+上传+迁移+重启） |
| CosyVoice AI 语音朗读 | ✅ | 生成式语音大模型（longanhuan 女声 / longanyang 男声），替换浏览器原生 SpeechSynthesis |
| Git 版本管理 | ✅ | GitHub: `laycz38/Vibe_AIFriends` |

---

## 项目结构

```
AIFriends/
├── README.md
├── CLAUDE.md                    # Claude Code 项目指南
├── deploy.py                    # 一键部署脚本
├── .gitignore
│
├── backend/                     # Django 后端
│   ├── manage.py
│   ├── requirements.txt         # Python 依赖（含 gunicorn）
│   ├── backend/
│   │   ├── settings.py          # CORS + JWT + 模板 + 环境变量
│   │   └── urls.py              # 根路由
│   └── web/
│       ├── models.py            # UserProfile / InterviewNote / Like / Favorite / Comment
│       ├── urls.py              # 17条 API 路由 + SPA fallback
│       ├── admin.py             # 5个模型后台注册
│       ├── views/
│       │   ├── index.py         # SPA fallback
│       │   ├── image_utils.py   # Base64 图片处理（压缩/转码）
│       │   ├── note/            # get_list / get_detail / create / toggle_like / toggle_favorite / favorite_list / create_comment
│       │   ├── chat/            # send_message / interview / sessions
│       │   ├── user/account/    # login / register / logout / refresh / info / update_profile
│       │   └── tts/             # synthesize（阿里云百炼 CosyVoice）
│       ├── utils/
│       │   └── aliyun_tts.py    # 百炼 CosyVoice WebSocket SDK 语音合成
│       └── migrations/          # 8个迁移
│
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── App.vue              # <NavBar><RouterView /></NavBar>
│   │   ├── main.js
│   │   ├── assets/main.css      # @import "tailwindcss" + @plugin "daisyui"
│   │   ├── data/notes.js        # 分类 + 菜单配置
│   │   ├── stores/user.js       # Pinia 用户状态
│   │   ├── js/http/api.js       # axios + 401 自动刷新
│   │   ├── components/
│   │   │   ├── navbar/          # NavBar.vue + UserMenu.vue + 6个 icons/
│   │   │   ├── FeedWaterfall.vue# Grid auto-fill 卡片网格
│   │   │   └── NoteCard.vue     # 240px 卡片 + hover scale-120 + ☆收藏
│   │   ├── views/
│   │   │   ├── homepage/HomepageIndex.vue
│   │   │   ├── note/NoteDetailIndex.vue  # card + chat + 点赞/收藏/评论
│   │   │   ├── create/CreateIndex.vue    # Base64 封面上传
│   │   │   ├── favorite/FavoriteIndex.vue# 收藏列表页
│   │   │   ├── friend/FriendIndex.vue
│   │   │   ├── profile/ProfileIndex.vue  # Base64 头像上传
│   │   │   ├── user/account/{Login,Register}Index.vue
│   │   │   ├── user/space/SpaceIndex.vue
│   │   │   └── error/NotFoundIndex.vue
│   │   └── router/index.js      # 11个路由 + 守卫
│   ├── vite.config.js           # port 5173 + build outDir
│   └── package.json
│
├── 项目文档/
│   ├── 项目架构文档.md            # 技术架构详解
│   ├── CLAUDE_DEPLOY.md          # 生产部署完整指南
│   └── Git提交记录.md             # Git 提交历史
│
└── Project_photo/                # 项目截图
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
| POST | `/api/user/account/update_profile/` | JWT | 更新头像(Base64)/简介 |

### AI 对话 & TTS
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/chat/send/` | JWT | DeepSeek 自由对话 |
| POST | `/api/chat/interview/` | JWT | DeepSeek 模拟面试（基于面经） |
| POST | `/api/tts/synthesize/` | JWT | 阿里云 TTS 语音合成，返回 base64 MP3 |

### 面经
| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/notes/` | 无 | 面经列表（`?search_query=` 搜索） |
| GET | `/api/notes/favorites/` | JWT | 我的收藏列表 |
| POST | `/api/notes/create/` | JWT | 发布面经（JSON + Base64 封面） |
| GET | `/api/notes/<id>/` | 无 | 面经详情（含 `favorited` 字段） |
| POST | `/api/notes/<id>/toggle_like/` | JWT | 点赞/取消 |
| POST | `/api/notes/<id>/toggle_favorite/` | JWT | 收藏/取消 |
| POST | `/api/notes/<id>/comments/create/` | JWT | 发表评论 |

---

## 数据模型（5个）

| 模型 | 关系 | 关键字段 |
|------|------|---------|
| **UserProfile** | 1:1 User | `photo_base64`(TextField), `bio` |
| **InterviewNote** | FK User | `cover_base64`(TextField), title, company, position, difficulty, likes |
| **InterviewNoteLike** | FK User + FK Note | unique(user, note) |
| **InterviewNoteFavorite** | FK User + FK Note | unique(user, note), `created_at` |
| **InterviewNoteComment** | FK User + FK Note | content |

> 图片存储方式：所有用户头像和面经封面以 Base64 字符串存入数据库 TextField，而非文件系统。
> 上传时自动压缩至 1200px 以内，详见 `web/views/image_utils.py`。

---

## 环境变量

配置 `backend/.env`：

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True

# DeepSeek（AI 对话）
DEEPSEEK_API_KEY=sk-your-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# 阿里云百炼 CosyVoice TTS（语音朗读，可选）
# API Key 在 https://bailian.console.aliyun.com/ → 模型广场 → API-KEY 管理 获取
DASHSCOPE_API_KEY=sk-
```

> CosyVoice 为可选功能。若不配置，会自动回退到浏览器原生语音合成。
> 默认音色：`longanhuan`（龙安欢，元气女声）和 `longanyang`（龙安洋，阳光男声）。

---

## 常用命令

```bash
# 开发：后端
cd backend && python manage.py runserver

# 开发：前端（HMR 热更新）
cd frontend && npm run dev          # → localhost:5173

# 生产：一键部署
python deploy.py                    # 构建+上传+迁移+重启

# 生产：分步构建
cd frontend && npm run build
# 上传 backend/ 到服务器，详见 CLAUDE_DEPLOY.md
```

---

## 参考文档

| 文档 | 路径 |
|------|------|
| 技术架构 | [项目文档/项目架构文档.md](项目文档/项目架构文档.md) |
| 部署指南 | [项目文档/CLAUDE_DEPLOY.md](项目文档/CLAUDE_DEPLOY.md) |
| Git 历史 | [项目文档/Git提交记录.md](项目文档/Git提交记录.md) |
| Claude Code 指南 | [CLAUDE.md](CLAUDE.md) |
