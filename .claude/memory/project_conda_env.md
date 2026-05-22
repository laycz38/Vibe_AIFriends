---
name: project_conda_env
description: 本项目的 conda 虚拟环境路径和激活方式
metadata:
  type: reference
---

conda 安装路径: `D:\coding_software\anaconda3\`
本项目虚拟环境名: `vibe_AIFriends`
环境目录: `D:\coding_software\anaconda3\envs\vibe_AIFriends\`
Python 路径: `D:\coding_software\anaconda3\envs\vibe_AIFriends\python.exe`

## 激活方式

```bash
# 方式一：初始化后激活
& "D:\coding_software\anaconda3\Scripts\conda.exe" init powershell
conda activate vibe_AIFriends

# 方式二：直接用完整路径（不用激活）
D:\coding_software\anaconda3\envs\vibe_AIFriends\python.exe manage.py runserver
```

## pip 安装包

```bash
D:\coding_software\anaconda3\envs\vibe_AIFriends\python.exe -m pip install <package>
```
