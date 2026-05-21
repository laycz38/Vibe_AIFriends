"""
AI面经 一键部署脚本

用法:
  python deploy.py                    # 完整部署（构建前端 + 上传代码 + 数据库迁移 + 重启服务）
  python deploy.py --skip-build       # 跳过前端构建，只上传代码和重启服务
  python deploy.py --skip-upload      # 只执行远程命令（迁移 + 重启）
  python deploy.py --migrate-only     # 只做数据库迁移和静态文件收集
  python deploy.py --restart          # 只重启 Gunicorn

前置条件：
  - 本地安装 Python（需要 paramiko 库）
  - 已配置好服务器 SSH 信息（见下面的 CONFIG）
  - 前端代码在 frontend/，后端代码在 backend/
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path

# ══════════════════════════════════════════
#  配置 —— 修改这里
# ══════════════════════════════════════════

CONFIG = {
    # 服务器连接
    "host": "121.43.36.186",
    "username": "acs",
    "password": "12138",
    # 远程路径
    "remote_root": "/home/acs/aifriends/backend/",
    "remote_venv_python": "/home/acs/aifriends/backend/venv/bin/python",
    "remote_venv_pip": "/home/acs/aifriends/backend/venv/bin/pip",
    # Gunicorn socket
    "gunicorn_sock": "/home/acs/aifriends/backend/gunicorn.sock",
    # 项目根目录（部署脚本所在目录）
    "project_root": os.path.dirname(os.path.abspath(__file__)),
}

# ══════════════════════════════════════════
#  工具函数
# ══════════════════════════════════════════

import io

# 强制 stdout 使用 UTF-8，解决 Windows GBK 编码问题
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
elif not isinstance(sys.stdout, io.TextIOWrapper):
    pass

def log(step, msg):
    print(f"\n[===== {step} {'='*30}]")
    print(f"  {msg}")

def run_local(cmd, cwd=None):
    """本地执行命令"""
    result = subprocess.run(cmd, shell=True, cwd=cwd or CONFIG["project_root"])
    if result.returncode != 0:
        print(f"  ❌ 命令失败: {cmd}")
        sys.exit(1)
    return result

def get_ssh_client():
    """创建 SSH 连接"""
    try:
        import paramiko
    except ImportError:
        print("❌ 需要安装 paramiko：pip install paramiko")
        sys.exit(1)

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print(f"  🔗 连接服务器 {CONFIG['host']}...")
    client.connect(
        CONFIG["host"],
        username=CONFIG["username"],
        password=CONFIG["password"],
        timeout=10,
    )
    print(f"  ✅ 已连接")
    return client

def ssh_run(client, command, title=""):
    """在远程服务器执行命令"""
    if title:
        print(f"  ⚡ {title}")
    stdin, stdout, stderr = client.exec_command(command, timeout=120)
    exit_status = stdout.channel.recv_exit_status()
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()
    if output:
        print(f"  {output}")
    if error and exit_status != 0:
        print(f"  ⚠️  {error}")
    return exit_status, output, error

def sftp_upload(client, local_dir, remote_dir, excludes=None):
    """通过 SFTP 上传目录"""
    local_dir = Path(local_dir)
    excludes = excludes or []
    total = 0

    with client.open_sftp() as sftp:
        # 确保远程目录存在
        _sftp_mkdir_p(sftp, remote_dir)

        for root, dirs, files in os.walk(local_dir):
            # 跳过排除目录
            rel = Path(root).relative_to(local_dir)
            if any(str(rel).startswith(e) for e in excludes):
                continue
            dirs[:] = [d for d in dirs if d not in excludes]

            for file in files:
                local_path = Path(root) / file
                remote_path = f"{remote_dir}/{rel / file}".replace("\\", "/")
                _sftp_mkdir_p(sftp, str(Path(remote_path).parent))

                sftp.put(str(local_path), remote_path)
                total += 1

    print(f"  📦 上传完成：{total} 个文件")

def _sftp_mkdir_p(sftp, remote_dir):
    """递归创建远程目录"""
    parts = remote_dir.replace("\\", "/").strip("/").split("/")
    path = ""
    for part in parts:
        path = f"{path}/{part}" if path else f"/{part}"
        try:
            sftp.stat(path)
        except FileNotFoundError:
            sftp.mkdir(path)

# ══════════════════════════════════════════
#  部署步骤
# ══════════════════════════════════════════

def step_build_frontend():
    """构建前端"""
    log("STEP 1/4", "构建前端")
    frontend_dir = Path(CONFIG["project_root"]) / "frontend"
    if not (frontend_dir / "package.json").exists():
        print("  ⚠️  未找到 frontend/package.json，跳过构建")
        return
    run_local("npm run build", cwd=str(frontend_dir))
    print("  ✅ 前端构建完成")

def step_upload():
    """上传代码到服务器"""
    log("STEP 2/4", "上传代码到服务器")

    excludes = [
        "__pycache__",
        "venv",
        ".venv",
        "db.sqlite3",
        ".env",
    ]

    client = get_ssh_client()
    try:
        # 先备份数据库
        log("备份", "备份远程数据库")
        ts = subprocess.run(
            ["date", "+%Y%m%d_%H%M%S"],
            capture_output=True, text=True
        ).stdout.strip()
        if not ts:
            import datetime
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ssh_run(client,
            f"cp {CONFIG['remote_root']}db.sqlite3 {CONFIG['remote_root']}db.sqlite3.{ts}.bak",
            title="备份 db.sqlite3")

        # 上传
        local_backend = Path(CONFIG["project_root"]) / "backend"
        sftp_upload(client, str(local_backend), CONFIG["remote_root"], excludes)
    finally:
        client.close()

    print("  ✅ 上传完成")

def step_server_setup():
    """服务器端：迁移 + 静态文件 + 安装依赖"""
    log("STEP 3/4", "服务器环境设置")

    client = get_ssh_client()
    try:
        # 检查是否有新依赖
        print("  ⚡ 检查并安装依赖...")
        ssh_run(client,
            f"cd {CONFIG['remote_root']} && {CONFIG['remote_venv_pip']} install -i "
            f"https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com "
            f"-r requirements.txt",
            title="pip install")

        # 数据库迁移
        ssh_run(client,
            f"cd {CONFIG['remote_root']} && {CONFIG['remote_venv_python']} manage.py migrate",
            title="数据库迁移")

        # 收集静态文件
        ssh_run(client,
            f"cd {CONFIG['remote_root']} && mkdir -p static && "
            f"{CONFIG['remote_venv_python']} manage.py collectstatic --noinput",
            title="收集静态文件")

    finally:
        client.close()

    print("  ✅ 服务器环境设置完成")

def step_restart():
    """重启 Gunicorn"""
    log("STEP 4/4", "重启 Gunicorn 服务")

    secret_key = os.environ.get("DJANGO_SECRET_KEY",
        "django-insecure-ft9=+wgt^=mzdw%d58j^f$tkp)lxc3%)1d%auhs%m6qrll#*r5")

    client = get_ssh_client()
    try:
        # Kill 旧进程
        ssh_run(client,
            f"ps aux | grep gunicorn | grep -v grep | awk '{{print $2}}' | xargs -r kill -9",
            title="停止旧 Gunicorn")
        ssh_run(client,
            f"rm -f {CONFIG['gunicorn_sock']}",
            title="清理旧 socket")

        # 在服务器上创建启动脚本（避免 bash 特殊字符逃逸问题）
        launch_script = (
            f"#!/bin/bash\n"
            f"cd {CONFIG['remote_root']}\n"
            f"export DJANGO_SECRET_KEY='{secret_key}'\n"
            f"export DJANGO_DEBUG=False\n"
            f"exec {CONFIG['remote_venv_python']} -m gunicorn --workers 3 "
            f"--graceful-timeout 30 "
            f"--bind unix:{CONFIG['gunicorn_sock']} "
            f"backend.wsgi:application\n"
        )
        remote_script = f"{CONFIG['remote_root']}start_gunicorn.sh"
        with client.open_sftp() as sftp:
            with sftp.open(remote_script, 'w') as f:
                f.write(launch_script)
        ssh_run(client, f"chmod +x {remote_script}", title="设置启动脚本权限")

        # 删除旧 tmux 会话，创建新会话并启动
        ssh_run(client,
            f"tmux kill-session -t aifriends 2>/dev/null; "
            f"tmux new-session -d -s aifriends",
            title="创建 tmux 会话")
        ssh_run(client,
            f"tmux send-keys -t aifriends '{remote_script}' Enter",
            title="启动 Gunicorn（tmux）")

        # 验证
        import time
        time.sleep(2)
        exit_code, out, err = ssh_run(client,
            f"ps aux | grep gunicorn | grep -v grep | head -3",
            title="验证 Gunicorn 运行状态")
        if "gunicorn" in out:
            print(f"  [OK] Gunicorn 已启动")
        else:
            print(f"  [WARN] Gunicorn 可能未启动。查看日志：tmux attach -t aifriends")

        # Nginx 重载
        ssh_run(client,
            f"echo '{CONFIG['password']}' | sudo -S nginx -t && "
            f"echo '{CONFIG['password']}' | sudo -S nginx -s reload",
            title="Nginx 重载配置")

    finally:
        client.close()

    print("\n" + "=" * 50)
    print("  ✅  部署完成！")
    print(f"  🌐  https://app6809.acapp.acwing.com.cn")
    print("=" * 50 + "\n")

# ══════════════════════════════════════════
#  CLI 入口
# ══════════════════════════════════════════

if __name__ == "__main__":
    args = sys.argv[1:]

    if "--migrate-only" in args:
        step_server_setup()
        sys.exit(0)

    if "--restart" in args:
        step_restart()
        sys.exit(0)

    if "--skip-build" not in args:
        step_build_frontend()

    if "--skip-upload" not in args:
        step_upload()

    step_server_setup()
    step_restart()
