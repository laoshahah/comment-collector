"""
自动更新模块
检查 GitHub Release 获取新版本
"""
import json
import os
import sys
import urllib.request
import zipfile
import shutil
from pathlib import Path
from typing import Optional, Callable
from packaging import version


# GitHub 仓库信息
GITHUB_OWNER = "laoshahah"
GITHUB_REPO = "comment-collector"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

# 从 config 导入版本号
try:
    from config import __version__ as CURRENT_VERSION
except ImportError:
    CURRENT_VERSION = "1.0.0"


class UpdateInfo:
    """更新信息"""
    def __init__(self, version: str, url: str, notes: str):
        self.version = version
        self.url = url
        self.notes = notes


def check_for_update() -> Optional[UpdateInfo]:
    """
    检查是否有新版本
    Returns:
        UpdateInfo 如果有更新，None 如果已是最新
    """
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"Accept": "application/vnd.github.v3+json"}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        latest_version = data["tag_name"].lstrip("v")

        if version.parse(latest_version) > version.parse(CURRENT_VERSION):
            # 找到对应平台的下载链接
            download_url = None
            assets = data.get("assets", [])

            if sys.platform == "darwin":
                # macOS: 查找 .dmg 或 .zip
                for asset in assets:
                    if asset["name"].endswith(".dmg") or "mac" in asset["name"].lower():
                        download_url = asset["browser_download_url"]
                        break
            elif sys.platform == "win32":
                # Windows: 查找 .exe 或 .zip
                for asset in assets:
                    if asset["name"].endswith(".zip") or "win" in asset["name"].lower():
                        download_url = asset["browser_download_url"]
                        break

            if download_url:
                return UpdateInfo(
                    version=latest_version,
                    url=download_url,
                    notes=data.get("body", "无更新说明"),
                )

    except Exception as e:
        print(f"检查更新失败: {e}")

    return None


def download_update(
    update_info: UpdateInfo,
    progress_callback: Callable[[int, int], None] = None,
) -> Optional[str]:
    """
    下载更新文件
    Args:
        update_info: 更新信息
        progress_callback: 进度回调 (downloaded, total)
    Returns:
        下载文件路径，失败返回 None
    """
    try:
        # 下载目录
        download_dir = Path.home() / "Downloads"
        download_dir.mkdir(exist_ok=True)

        # 文件名
        filename = update_info.url.split("/")[-1]
        filepath = download_dir / filename

        # 下载文件
        req = urllib.request.Request(update_info.url)
        with urllib.request.urlopen(req) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            downloaded = 0

            with open(filepath, "wb") as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)

                    if progress_callback and total_size > 0:
                        progress_callback(downloaded, total_size)

        print(f"下载完成: {filepath}")
        return str(filepath)

    except Exception as e:
        print(f"下载更新失败: {e}")
        return None


def apply_update(zip_path: str) -> bool:
    """
    应用更新（解压并替换当前应用）
    Args:
        zip_path: 下载的 zip 文件路径
    Returns:
        是否成功
    """
    try:
        # 获取当前应用目录
        if getattr(sys, "frozen", False):
            # 打包后的应用
            app_dir = Path(sys.executable).parent
        else:
            # 开发环境
            app_dir = Path(__file__).parent.parent

        # 备份当前版本
        backup_dir = app_dir.parent / "backup"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        shutil.copytree(app_dir, backup_dir)

        # 解压新版本
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # 解压到临时目录
            temp_dir = app_dir.parent / "temp_update"
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            zip_ref.extractall(temp_dir)

            # 复制文件到应用目录
            extracted_dir = list(temp_dir.iterdir())[0]
            if extracted_dir.is_dir():
                for item in extracted_dir.iterdir():
                    dest = app_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(item), str(dest))

            # 清理临时目录
            shutil.rmtree(temp_dir)

        print("更新应用成功！")
        return True

    except Exception as e:
        print(f"应用更新失败: {e}")
        # 尝试恢复备份
        if backup_dir.exists():
            shutil.rmtree(app_dir)
            shutil.copytree(backup_dir, app_dir)
            print("已恢复到旧版本")
        return False


def restart_app():
    """重启应用"""
    if getattr(sys, "frozen", False):
        # 打包后的应用
        app_path = sys.executable
    else:
        # 开发环境
        app_path = sys.argv[0]

    os.execv(sys.executable, [sys.executable] + sys.argv)
