---
name: feedback_docs_and_git_workflow
description: 代码改动后同步更新文档并 git commit + push
metadata:
  type: feedback
---

每次有意义的代码改动后，同步更新相关文档（README.md、项目架构文档.md、CLAUDE.md），然后构建前端、git commit、git push。

**Why:** 用户多次强调"帮我更新一下需要更新的文档，然后上传git"，这是一个已验证的工作流偏好。文档和代码应保持同步。

**How to apply:**
1. 代码改动完成后，检查 README.md / 项目架构文档.md / CLAUDE.md 是否需要更新
2. 更新技术栈、架构图、依赖列表、日期等
3. `npm run build` 构建前端
4. `git add` 具体文件（不用 `-A`），排除本地配置
5. `git commit` + `git push`
