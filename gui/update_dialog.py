"""
更新对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QProgressBar, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from updater.updater import (
    check_for_update, download_update, apply_update,
    restart_app, UpdateInfo
)


class UpdateCheckThread(QThread):
    """检查更新线程"""
    update_available = pyqtSignal(object)  # UpdateInfo or None
    error = pyqtSignal(str)

    def run(self):
        try:
            update_info = check_for_update()
            self.update_available.emit(update_info)
        except Exception as e:
            self.error.emit(str(e))


class DownloadThread(QThread):
    """下载更新线程"""
    progress = pyqtSignal(int, int)  # downloaded, total
    finished = pyqtSignal(str)  # file path
    error = pyqtSignal(str)

    def __init__(self, update_info: UpdateInfo):
        super().__init__()
        self.update_info = update_info

    def run(self):
        try:
            filepath = download_update(
                self.update_info,
                progress_callback=lambda d, t: self.progress.emit(d, t)
            )
            if filepath:
                self.finished.emit(filepath)
            else:
                self.error.emit("下载失败")
        except Exception as e:
            self.error.emit(str(e))


class UpdateDialog(QDialog):
    """更新对话框"""

    def __init__(self, parent=None, auto_check: bool = False):
        super().__init__(parent)
        self.auto_check = auto_check
        self.update_info = None
        self.download_thread = None
        self.init_ui()

        if auto_check:
            self.check_update()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("检查更新")
        self.setMinimumWidth(400)

        layout = QVBoxLayout(self)

        # 状态标签
        self.status_label = QLabel("正在检查更新...")
        self.status_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.status_label)

        # 版本信息
        self.version_label = QLabel("")
        layout.addWidget(self.version_label)

        # 更新说明
        self.notes_text = QTextEdit()
        self.notes_text.setReadOnly(True)
        self.notes_text.setMaximumHeight(150)
        self.notes_text.hide()
        layout.addWidget(self.notes_text)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # 按钮
        btn_layout = QHBoxLayout()

        self.check_btn = QPushButton("检查更新")
        self.check_btn.clicked.connect(self.check_update)
        btn_layout.addWidget(self.check_btn)

        self.download_btn = QPushButton("下载更新")
        self.download_btn.hide()
        self.download_btn.clicked.connect(self.start_download)
        btn_layout.addWidget(self.download_btn)

        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

    def check_update(self):
        """检查更新"""
        self.status_label.setText("正在检查更新...")
        self.check_btn.setEnabled(False)
        self.download_btn.hide()
        self.notes_text.hide()

        self.check_thread = UpdateCheckThread()
        self.check_thread.update_available.connect(self.on_update_checked)
        self.check_thread.error.connect(self.on_check_error)
        self.check_thread.start()

    def on_update_checked(self, update_info: UpdateInfo):
        """检查更新完成"""
        self.check_btn.setEnabled(True)

        if update_info:
            self.update_info = update_info
            self.status_label.setText(f"发现新版本: v{update_info.version}")
            self.version_label.setText(f"当前版本: v1.0.0")

            if update_info.notes:
                self.notes_text.setPlainText(update_info.notes)
                self.notes_text.show()

            self.download_btn.show()
        else:
            self.status_label.setText("已是最新版本！")
            self.version_label.setText("当前版本: v1.0.0")

            if self.auto_check:
                # 自动检查时不显示"已是最新"对话框
                self.close()

    def on_check_error(self, error_msg: str):
        """检查更新出错"""
        self.check_btn.setEnabled(True)
        self.status_label.setText(f"检查更新失败: {error_msg}")

        if self.auto_check:
            self.close()

    def start_download(self):
        """开始下载更新"""
        if not self.update_info:
            return

        self.download_btn.setEnabled(False)
        self.check_btn.setEnabled(False)
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        self.download_thread = DownloadThread(self.update_info)
        self.download_thread.progress.connect(self.on_download_progress)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.error.connect(self.on_download_error)
        self.download_thread.start()

    def on_download_progress(self, downloaded: int, total: int):
        """下载进度更新"""
        if total > 0:
            percent = int(downloaded / total * 100)
            self.progress_bar.setValue(percent)
            self.status_label.setText(f"下载中... {percent}%")

    def on_download_finished(self, filepath: str):
        """下载完成"""
        self.progress_bar.setValue(100)
        self.status_label.setText("下载完成！")

        reply = QMessageBox.question(
            self, "更新",
            "下载完成，是否立即安装更新？\n安装后应用将自动重启。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if apply_update(filepath):
                QMessageBox.information(
                    self, "更新成功",
                    "更新已应用，应用将自动重启。"
                )
                restart_app()
            else:
                QMessageBox.critical(
                    self, "更新失败",
                    "更新应用失败，请手动替换文件。"
                )

        self.close()

    def on_download_error(self, error_msg: str):
        """下载出错"""
        self.download_btn.setEnabled(True)
        self.check_btn.setEnabled(True)
        self.progress_bar.hide()
        self.status_label.setText(f"下载失败: {error_msg}")
