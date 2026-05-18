# AI 提示词文档

> 用途：记录项目中使用的 AI 生成提示词，方便后续复现和调整  
> 创建日期：2026-05-18

---

## 提示词一：小红书风格首页布局

### 使用场景
在已有 Vue3 + Vite + TailwindCSS4 + daisyUI 项目中，生成一个高还原度的小红书 Web 首页布局。

### 完整提示词

```
使用 Vue3 + Vite + TailwindCSS4 + daisyUI 实现一个"小红书风格"的首页布局，要求高还原度。

技术要求：
- Vue3 Composition API
- TailwindCSS 4
- 可使用 daisyUI
- 页面响应式
- 组件化开发
- 不使用 Element Plus
- 风格简洁，接近小红书 Web 首页

页面结构：
App
 ├── Sidebar（左侧固定 280px）
 ├── Header（顶部固定 72px）
 └── FeedWaterfall（瀑布流）
       └── NoteCard

Sidebar 包含：Logo、菜单项（发现/直播/发布/通知）、登录按钮、登录提示卡片、更多
Header 包含：居中搜索框（~600px）、分类 Tab（推荐/穿搭/美食等 11 项）、创作中心/业务合作
FeedWaterfall 使用 CSS columns 实现瀑布流，响应式 2-5 列
NoteCard 包含：图片、标题（两行省略）、作者头像+名称、爱心+点赞数

UI 风格：
- 主色 #ff2442
- 背景 #f7f7f7
- 圆角卡片 rounded-2xl
- hover 阴影 shadow-sm → shadow-lg + 上浮 -translate-y-1 + 图片放大 scale-105
- 禁止过重边框、花哨渐变、大面积颜色
- 极简、高级留白、现代感

数据：15 条 mock 笔记数据，包含图片/标题/作者/点赞数，用 v-for 渲染
```

### 生成结果
- [x] 6 个组件文件 + 1 个数据文件
- [x] 响应式瀑布流 2-5 列
- [x] daisyUI 集成
- [x] 小红书风格高还原

### 涉及文件
| 文件 | 说明 |
|------|------|
| `src/data/notes.js` | mock 数据 |
| `src/components/Sidebar.vue` | 侧边栏 |
| `src/components/Header.vue` | 顶部栏 |
| `src/components/FeedWaterfall.vue` | 瀑布流容器 |
| `src/components/NoteCard.vue` | 笔记卡片 |
| `src/App.vue` | 根组件整合 |
| `src/assets/main.css` | Tailwind + daisyUI + utility |

---

## 提示词模板：新页面/新功能

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
- [其他风格要求]
```

---

## 提示词模板：Django 后端接口

```
在现有 Django + DRF + SimpleJWT 项目中，实现 [功能描述]。

技术要求：
- Django REST Framework
- JWT 认证
- [其他要求]

数据模型：
[描述 Model 字段]

API 接口：
| 方法 | 路径 | 说明 |
[接口列表]

要求：
- 序列化器（Serializer）
- 视图（ViewSet / APIView）
- 路由注册
```

---

## 提示词使用记录

| # | 日期 | 提示词 | 状态 | 备注 |
|---|------|--------|------|------|
| 1 | 2026-05-18 | 小红书首页布局 | ✅ 完成 | 见上方「提示词一」 |
| 2 | - | - | ⬜ | - |
| 3 | - | - | ⬜ | - |

---

> 💡 使用方式：新开对话时，复制对应提示词，粘贴即可复现相同效果。根据实际需求微调参数和数据。
