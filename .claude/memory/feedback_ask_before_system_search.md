---
name: feedback_ask_before_system_search
description: 不要在系统盘执行大范围搜索，先问用户
metadata:
  type: feedback
---

不要在系统盘（C:、D: 根目录）执行大范围文件搜索来找 conda 或其他工具。用户拒绝了 `Get-ChildItem C:\Users\20818 -Directory` 的 PowerShell 搜索。

**Why:** 用户中断了系统范围的 conda 搜索，更倾向于直接提供路径信息。

**How to apply:** 需要找某个不在项目目录内的工具/路径时，先问用户，而不是在系统盘遍历搜索。用户知道自己的环境配置，直接提供更高效。
