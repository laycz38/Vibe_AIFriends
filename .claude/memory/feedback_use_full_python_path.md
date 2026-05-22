---
name: feedback_use_full_python_path
description: 在 bash 中用完整的 conda Python 路径来运行 Python 和 pip
metadata:
  type: feedback
---

始终使用完整 conda Python 路径来运行 Python 命令，因为 bash shell 中没有 conda 在 PATH 中。

**Why:** bash 中 `pip`、`python`、`conda` 命令均不可用，指向 Windows stub 或找不到。用户已确认 conda 环境位于 `D:\coding_software\anaconda3\envs\vibe_AIFriends\`。

**How to apply:** 所有 Python 操作使用全路径：

```bash
# Django
D:/coding_software/anaconda3/envs/vibe_AIFriends/python.exe manage.py runserver

# pip 安装
D:/coding_software/anaconda3/envs/vibe_AIFriends/python.exe -m pip install <package>

# 测试脚本
D:/coding_software/anaconda3/envs/vibe_AIFriends/python.exe -c "..."
```

Related: [[project_conda_env]]
