"""
跨平台评论采集与客户信息提取工具
主入口文件
"""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from gui.main_window import MainWindow
from utils.logger import logger


def main():
    """主函数"""
    # 设置环境变量
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"

    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("评论采集工具")
    app.setApplicationVersion("1.0.0")

    # 设置高DPI支持
    app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)

    # 创建主窗口
    try:
        window = MainWindow()
        window.show()
        logger.info("应用启动成功")
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"应用启动失败: {e}")
        raise


if __name__ == "__main__":
    main()
