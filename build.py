"""
打包脚本 - 将应用打包成可执行文件
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"已清理: {dir_name}")


def check_icon():
    """检查图标文件是否存在"""
    icon_dir = Path("assets")
    if sys.platform == "darwin":
        icon_file = icon_dir / "icon.icns"
    else:
        icon_file = icon_dir / "icon.ico"

    if icon_file.exists():
        return str(icon_file)
    else:
        print(f"警告: 图标文件不存在 ({icon_file})")
        print("运行 'python assets/generate_icon.py' 生成图标")
        return None


def build_mac():
    """打包 macOS 应用"""
    print("开始打包 macOS 应用...")

    icon_path = check_icon()

    # PyInstaller 参数
    cmd = [
        "pyinstaller",
        "--name=评论采集工具",
        "--windowed",  # 无控制台窗口
        "--onedir",    # 单目录打包
        "--noconfirm",
        "--clean",
        # 添加数据文件
        "--add-data=config.py:.",
        "--add-data=updater:updater",
        # 图标
        f"--icon={icon_path}" if icon_path else "",
        # 隐藏导入
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=playwright",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=sqlite3",
        "--hidden-import=packaging",
        # 排除不需要的模块
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        # 入口文件
        "main.py",
    ]

    # 过滤空字符串
    cmd = [c for c in cmd if c]

    subprocess.run(cmd, check=True)
    print("macOS 应用打包完成！")
    print(f"输出目录: dist/评论采集工具/")


def build_windows():
    """打包 Windows 应用"""
    print("开始打包 Windows 应用...")

    icon_path = check_icon()

    cmd = [
        "pyinstaller",
        "--name=CommentCollector",
        "--windowed",
        "--onedir",
        "--noconfirm",
        "--clean",
        "--add-data=config.py;.",
        "--add-data=updater;updater",
        f"--icon={icon_path}" if icon_path else "",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtWidgets",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=playwright",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=sqlite3",
        "--hidden-import=packaging",
        "--exclude-module=tkinter",
        "--exclude-module=matplotlib",
        "--exclude-module=numpy",
        "main.py",
    ]

    # 过滤空字符串
    cmd = [c for c in cmd if c]

    subprocess.run(cmd, check=True)
    print("Windows 应用打包完成！")
    print(f"输出目录: dist/CommentCollector/")


def create_installer_mac():
    """创建 macOS 安装包 (.dmg)"""
    print("创建 macOS 安装包...")

    # 创建 DMG
    cmd = [
        "hdiutil", "create",
        "-volname", "评论采集工具",
        "-srcfolder", "dist/评论采集工具",
        "-ov", "-format", "UDZO",
        "dist/评论采集工具.dmg",
    ]

    subprocess.run(cmd, check=True)
    print("macOS 安装包创建完成: dist/评论采集工具.dmg")


def main():
    """主函数"""
    # 切换到项目目录
    os.chdir(Path(__file__).parent)

    # 清理旧的构建文件
    clean_build()

    # 根据平台打包
    if sys.platform == "darwin":
        build_mac()
        # 可选：创建 DMG
        # create_installer_mac()
    elif sys.platform == "win32":
        build_windows()
    else:
        print(f"不支持的平台: {sys.platform}")
        sys.exit(1)

    print("\n打包完成！")
    print("\n下一步:")
    print("  1. 测试 dist/ 目录下的应用是否正常运行")
    print("  2. 创建 DMG 安装包: python build.py --dmg")
    print("  3. 上传到 GitHub Release 或网盘分发")


if __name__ == "__main__":
    if "--dmg" in sys.argv:
        create_installer_mac()
    else:
        main()
