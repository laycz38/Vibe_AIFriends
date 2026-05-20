# AI 提示词文档

> 用途：记录项目中使用的 AI 生成提示词，方便后续复现和调整  
> 创建日期：2026-05-18  
> 最后更新：2026-05-20

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

## 提示词八：项目主题改版 — 从小红书生活流到 AI 面经

### 使用场景
首页布局已有，需要将内容主题从"小红书生活"改为"AI 技术面经社区"。

### 用户输入
```
把前端从小红书生活分享改造成 AI 面经社区：
- Sidebar 品牌从"小红书"改为"AI 面经"
- 菜单改为：发现、AI 问答、发布面经、我的收藏
- Header 搜索 placeholder 改为"搜索面经、公司、岗位..."
- 分类Tab 改为：全部/前端/后端/算法/大数据/测试/运维/产品/设计/校招/实习
- NoteCard 增加 company、position、difficulty 字段
- mock 数据改成技术面经内容
- 整体色调从红色#ff2442转为indigo/紫色系
```

### 产出
| 文件 | 说明 |
|------|------|
| `src/data/notes.js` | 面经 mock 数据 + 技术分类 + AI 菜单 |
| `src/components/Sidebar.vue` | Logo 改为"AI 面经"，菜单更新 |
| `src/components/Header.vue` | 搜索 placeholder + 分类Tab 更新 |
| `src/components/NoteCard.vue` | 增加 company/difficulty/position 显示 |

### 状态
✅ 完成

---

## 提示词九：前端路由系统 + 页面骨架

### 使用场景
需要将单页面原型升级为多页面 Vue 应用。

### 用户输入
```
创建以下页面文件：
- HomepageIndex.vue、FriendIndex.vue、CreateIndex.vue
- NotFoundIndex.vue、LoginIndex.vue、RegisterIndex.vue
- SpaceIndex.vue（动态 user_id）、ProfileIndex.vue

在 router/index.js 中添加所有路由：
- / → HomepageIndex
- /friend/ → FriendIndex（requiresAuth）
- /create/ → CreateIndex（requiresAuth）
- /user/:user_id/ → SpaceIndex（props: true, requiresAuth）
- /user/account/login/ → LoginIndex
- /user/account/register/ → RegisterIndex
- /:pathMatch(.*)* → NotFoundIndex

在 App.vue 中用 RouterView 替换静态组件渲染
Header/Sidebar 菜单改为 RouterLink
添加 active-class 样式
```

### 产出
| 文件 | 说明 |
|------|------|
| `src/views/homepage/HomepageIndex.vue` | 首页容器 |
| `src/views/friend/FriendIndex.vue` | AI 面试预留 |
| `src/views/create/CreateIndex.vue` | 发布页预留 |
| `src/views/error/NotFoundIndex.vue` | 404 页 |
| `src/views/user/account/LoginIndex.vue` | 登录页预留 |
| `src/views/user/account/RegisterIndex.vue` | 注册页预留 |
| `src/views/user/space/SpaceIndex.vue` | 用户空间 |
| `src/views/profile/ProfileIndex.vue` | 资料页预留 |
| `src/router/index.js` | 10 个路由 + 动态参数 |
| `src/App.vue` | RouterView + Sidebar/Header 重构 |
| `src/components/Sidebar.vue` | RouterLink 替换 |
| `src/components/Header.vue` | RouterLink 替换 |

### 状态
✅ 完成

---

## 提示词十：用户认证系统（前后端完整实现）

### 使用场景
需要完整的用户注册、登录、退出、Token 刷新体系。

### 用户输入
```
后端：
创建 UserProfile 模型（1:1 User, photo=ImageField, bio=TextField）
实现 views/user/account/：
  login.py — 用户名+密码 → JWT + refresh cookie
  register.py — 创建用户 + 返回 token
  logout.py — 清除 refresh cookie
  refresh_token.py — 用 cookie 刷新 access token
  get_user_info.py — 返回当前用户信息（含头像、简介、统计）
  update_profile.py — 更新头像/简介（multipart）
  common.py — 用户序列化 + set_refresh_cookie 工具

前端：
创建 stores/user.js（Pinia）：
  - accessToken + user 持久化到 localStorage
  - isLoggedIn getter
  - login/register/pullUserInfo/updateProfile/refreshToken/logout actions
  - hasPulledUserInfo 防重复拉取标记

创建 js/http/api.js（axios 封装）：
  - 自动添加 Authorization header
  - 401 自动用 refresh_token 刷新（队列机制防并发）
  - 开发/生产环境 BASE_URL 区分

路由添加守卫：
  beforeEach 检查 requiresAuth + hasPulledUserInfo + isLoggedIn

App.vue onMounted：
  先 pullUserInfo()，再检查是否需要 router.replace 到 login
```

### 产出
| 文件 | 说明 |
|------|------|
| `backend/web/models.py` | UserProfile 模型 |
| `backend/web/views/user/account/*.py` | 6 个认证视图 + common.py |
| `backend/web/urls.py` | 6 个认证路由 |
| `backend/web/admin.py` | UserProfile 注册到后台 |
| `frontend/src/stores/user.js` | Pinia 用户状态管理 |
| `frontend/src/js/http/api.js` | axios 封装 + 拦截器 |
| `frontend/src/router/index.js` | 路由守卫 |
| `frontend/src/App.vue` | 首屏拉取用户信息 |
| `frontend/src/components/Header.vue` | 登录态按钮切换 |
| `frontend/src/components/Sidebar.vue` | 登录态按钮切换 |

### 状态
✅ 完成

---

## 提示词十一：面经内容系统 + 真实数据替换 Mock

### 使用场景
需要用户能真正发布面经、首页展示真实数据。

### 用户输入
```
后端：
创建 InterviewNote 模型：
  user(FK), title, content, cover(ImageField), company, position, difficulty
创建 InterviewNoteLike 模型（unique user+note）
创建 InterviewNoteComment 模型
实现 views/note/：
  get_list.py — 首页面经列表（按时间倒序）
  create.py — 发布面经（multipart FormData，支持封面）
  get_detail.py — 面经详情（含 like 状态 + 评论列表）
  toggle_like.py — 点赞/取消（toggle）
  create_comment.py — 发表评论
  common.py — 笔记序列化工具

前端：
FeedWaterfall.vue 改为从 api 拉取真实数据（替代 mock）
NoteCard.vue 封面点击跳转到 /notes/:id/
创建 NoteDetailIndex.vue：
  - 加载详情
  - 点赞按钮（未登录跳登录）
  - 评论区（发表 + 列表）
CreateIndex.vue 实现真实发布：
  - FormData 上传封面
  - 标题/内容/公司/岗位/难度表单
  - 封面预览
```

### 产出
| 文件 | 说明 |
|------|------|
| `backend/web/models.py` | 新增 InterviewNote/Like/Comment 模型 |
| `backend/web/views/note/*.py` | 5 个面经视图 + common.py |
| `backend/web/urls.py` | 5 个面经路由 |
| `backend/web/admin.py` | 3 个模型注册到后台 |
| `frontend/src/components/FeedWaterfall.vue` | API 数据替换 mock |
| `frontend/src/views/note/NoteDetailIndex.vue` | 新建，面经详情页 |
| `frontend/src/views/create/CreateIndex.vue` | 真实发布表单 |
| `frontend/src/components/NoteCard.vue` | 封面点击跳详情 |
| `frontend/src/router/index.js` | /notes/:note_id/ 路由 |

### 状态
✅ 完成

---

## 提示词十二：封面图片上传 + MEDIA_URL 修复

### 使用场景
需要从 URL 封面改为本地图片上传，并修复媒体文件地址问题。

### 用户输入
```
把 cover_url 改为 ImageField（cover），支持本地图片上传
前端 CreateIndex.vue 改用 FormData 上传封面（input type=file）
upload_to='notes/covers/'
MEDIA_URL 从 'http://127.0.0.1:8000/media/' 改为 '/media/'（相对路径）
```

### 产出
| 文件 | 说明 |
|------|------|
| `backend/web/models.py` | cover_url → cover(ImageField) |
| `backend/web/views/note/create.py` | request.FILES.get('cover') |
| `backend/backend/settings.py` | MEDIA_URL = '/media/' |
| `frontend/src/views/create/CreateIndex.vue` | FormData 上传 + 预览 |

### 状态
✅ 完成

---

## 提示词十三：用户头像 + 个人资料 + 右上角菜单

### 使用场景
需要右上角显示用户头像、支持编辑个人资料、点击头像出现下拉菜单。

### 用户输入
```
创建 UserMenu.vue：右上角头像下拉
  - 头像（来自数据库 /media/avatars/）
  - 用户名、简介预览
  - 编辑资料 / 我的空间 / 退出登录
  - 点击外部关闭

创建 ProfileIndex.vue：资料编辑页
  - 上传头像（FormData + 预览）
  - 编辑简介（textarea）
  - 显示统计数据（面经数、评论数、点赞数）

Header.vue 集成 UserMenu（登录后显示）
```

### 产出
| 文件 | 说明 |
|------|------|
| `frontend/src/components/navbar/UserMenu.vue` | 用户头像下拉菜单 |
| `frontend/src/views/profile/ProfileIndex.vue` | 资料编辑页 |
| `frontend/src/components/Header.vue` | 集成 UserMenu |
| `backend/web/views/user/account/update_profile.py` | 头像+简介更新 |

### 状态
✅ 完成

---

## 提示词十四：Django 托管前端 + 生产环境同源修复

### 使用场景
需要 Django 同时服务前后端，并修复打包后首页加载失败问题。

### 用户输入
```
settings.py 添加 TEMPLATES DIRS → static/frontend/
创建 views/index.py：render index.html
urls.py 添加根路径和 re_path fallback
前端 api.js 改为开发环境用 127.0.0.1:8000，生产环境用相对路径 ''
Vite 配置固定端口 5173 + strictPort: true
```

### 产出
| 文件 | 说明 |
|------|------|
| `backend/backend/settings.py` | TEMPLATES DIRS |
| `backend/web/views/index.py` | SPA fallback 视图 |
| `backend/web/urls.py` | 根路径 + re_path fallback |
| `frontend/src/js/http/api.js` | DEV 判断 BASE_URL |
| `frontend/vite.config.js` | port + strictPort |

### 状态
✅ 完成

---

## 提示词十五：左侧栏伸缩布局

### 使用场景
需要实现点击 Header 左上角按钮时，左侧栏从窄栏（仅图标）切换为宽栏（图标+文字）。

### 用户输入
```
在 App.vue 中：
  添加 isSidebarExpanded ref（默认 false）
  添加 toggleSidebar 函数
  Sidebar 传递 :expanded prop
  Header 传递 @toggle-sidebar 事件
  main 根据 isSidebarExpanded 动态切换 pl-[72px] / pl-[220px]

在 Header.vue 中：
  左上角添加菜单按钮
  emit('toggle-sidebar')

在 Sidebar.vue 中：
  接收 expanded prop
  宽度在 72px（收起）/ 220px（展开）之间切换
  收起时只显示图标，展开时显示文字
```

### 产出
| 文件 | 说明 |
|------|------|
| `frontend/src/App.vue` | isSidebarExpanded 状态 + 动态布局 |
| `frontend/src/components/Header.vue` | 菜单按钮 + emit（待完成） |
| `frontend/src/components/Sidebar.vue` | expanded prop + 宽度切换（待完成） |

### 状态
🔧 进行中（App.vue 已完成，Header/Sidebar 样式对接中）

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
[描述 API 接口和数据格式]

UI 风格：
- 主色 indigo/紫色系
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
| 8 | 2026-05-20 | 项目改版 AI 面经 | ✅ | 品牌/菜单/分类/色调全面改造 |
| 9 | 2026-05-20 | 前端路由 + 页面骨架 | ✅ | 10个页面 + 动态路由 + 404 |
| 10 | 2026-05-20 | 用户认证系统 | ✅ | 注册/登录/退出/刷新 + Pinia + axios拦截器 |
| 11 | 2026-05-20 | 面经内容系统 | ✅ | CRUD + 点赞 + 评论 + 真实数据 |
| 12 | 2026-05-20 | 封面图片上传 | ✅ | ImageField + FormData + MEDIA_URL |
| 13 | 2026-05-20 | 用户头像 + 资料 | ✅ | UserMenu + ProfileIndex |
| 14 | 2026-05-20 | Django托管 + 同源修复 | ✅ | SPA fallback + api.js DEV判断 |
| 15 | 2026-05-20 | 左侧栏伸缩布局 | 🔧 | App.vue完成，Header/Sidebar对接中 |

---

> 💡 **使用方式**：新开对话时，复制对应提示词，粘贴即可复现相同效果。根据实际需求微调参数和数据。
