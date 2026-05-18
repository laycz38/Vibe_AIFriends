# AIFriends

一个前后端分离的 Web 项目，使用 Django + Vue 3 构建。

## 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 后端 | Django 6.0 + DRF | REST API + JWT 认证 |
| 前端 | Vue 3 + Vite | SPA 单页面应用 |
| 数据库 | SQLite | 开发环境 |

## 快速开始

### 后端

```bash
cd backend
python manage.py runserver
```

访问 `http://127.0.0.1:8000/`

### 前端

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173/`

## 项目结构

```
AIFriends/
├── backend/          # Django 后端
├── frontend/         # Vue 3 前端（小红书风格首页）
├── 项目文档/          # 📁 项目参考文档
│   ├── 项目架构文档.md
│   ├── 学习笔记.md
│   ├── AI提示词文档.md
│   └── Git提交记录.md
└── README.md
```
