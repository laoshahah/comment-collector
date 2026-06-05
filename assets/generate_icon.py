"""
图标生成脚本
将 SVG 转换为 macOS (.icns) 和 Windows (.ico) 图标格式
"""
import os
import subprocess
from pathlib import Path


def create_png_from_svg(svg_path: str, png_path: str, size: int = 512):
    """使用 rsvg-convert 将 SVG 转换为 PNG"""
    cmd = [
        "rsvg-convert",
        "-w", str(size),
        "-h", str(size),
        svg_path,
        "-o", png_path,
    ]
    subprocess.run(cmd, check=True)
    print(f"已生成 PNG: {png_path}")


def create_icns(png_path: str, icns_path: str):
    """使用 iconutil 创建 macOS .icns 文件"""
    # 创建临时 iconset 目录
    iconset_dir = Path("icon.iconset")
    iconset_dir.mkdir(exist_ok=True)

    # 生成不同尺寸的图标
    sizes = [16, 32, 64, 128, 256, 512]
    for size in sizes:
        # 标准尺寸
        cmd = [
            "sips", "-z", str(size), str(size),
            png_path,
            "--out", str(iconset_dir / f"icon_{size}x{size}.png"),
        ]
        subprocess.run(cmd, check=True)

        # @2x 尺寸（Retina）
        if size <= 256:
            cmd = [
                "sips", "-z", str(size * 2), str(size * 2),
                png_path,
                "--out", str(iconset_dir / f"icon_{size}x{size}@2x.png"),
            ]
            subprocess.run(cmd, check=True)

    # 使用 iconutil 创建 icns
    cmd = ["iconutil", "-c", "icns", str(iconset_dir), "-o", icns_path]
    subprocess.run(cmd, check=True)

    # 清理临时目录
    import shutil
    shutil.rmtree(iconset_dir)

    print(f"已生成 ICNS: {icns_path}")


def create_ico(png_path: str, ico_path: str):
    """使用 Pillow 创建 Windows .ico 文件"""
    try:
        from PIL import Image

        img = Image.open(png_path)
        sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save(ico_path, format="ICO", sizes=sizes)
        print(f"已生成 ICO: {ico_path}")
    except ImportError:
        print("需要安装 Pillow: pip install Pillow")


def main():
    os.chdir(Path(__file__).parent)

    svg_path = "icon.svg"
    png_path = "icon.png"
    icns_path = "icon.icns"
    ico_path = "icon.ico"

    # 1. SVG -> PNG
    print("步骤 1: 生成 PNG...")
    create_png_from_svg(svg_path, png_path)

    # 2. PNG -> ICNS (macOS)
    print("\n步骤 2: 生成 macOS 图标...")
    create_icns(png_path, icns_path)

    # 3. PNG -> ICO (Windows)
    print("\n步骤 3: 生成 Windows 图标...")
    create_ico(png_path, ico_path)

    print("\n图标生成完成！")
    print(f"  - macOS: {icns_path}")
    print(f"  - Windows: {ico_path}")


if __name__ == "__main__":
    main()
