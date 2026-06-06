"""
设置对话框
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QSpinBox, QCheckBox, QComboBox,
    QPushButton, QGroupBox, QFormLayout, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt
from config import CRAWLER_CONFIG, EXPORT_DIR, save_settings, load_settings


class SettingsDialog(QDialog):
    """设置对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(500)
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 爬虫设置组
        crawler_group = QGroupBox("爬虫设置")
        crawler_layout = QFormLayout(crawler_group)

        self.min_delay_spin = QSpinBox()
        self.min_delay_spin.setRange(1, 30)
        self.min_delay_spin.setSuffix(" 秒")
        crawler_layout.addRow("最小延时:", self.min_delay_spin)

        self.max_delay_spin = QSpinBox()
        self.max_delay_spin.setRange(1, 60)
        self.max_delay_spin.setSuffix(" 秒")
        crawler_layout.addRow("最大延时:", self.max_delay_spin)

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 120)
        self.timeout_spin.setSuffix(" 秒")
        crawler_layout.addRow("超时时间:", self.timeout_spin)

        self.headless_check = QCheckBox("无头模式（不显示浏览器窗口）")
        crawler_layout.addRow("", self.headless_check)

        layout.addWidget(crawler_group)

        # 导出设置组
        export_group = QGroupBox("导出设置")
        export_layout = QFormLayout(export_group)

        self.export_path_edit = QLineEdit()
        self.export_path_edit.setReadOnly(True)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.export_path_edit)
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_export_path)
        path_layout.addWidget(browse_btn)
        export_layout.addRow("导出路径:", path_layout)

        layout.addWidget(export_group)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.save_settings)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("background-color: #757575;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def load_settings(self):
        """加载当前设置"""
        self.min_delay_spin.setValue(CRAWLER_CONFIG["min_delay"])
        self.max_delay_spin.setValue(CRAWLER_CONFIG["max_delay"])
        self.timeout_spin.setValue(CRAWLER_CONFIG["timeout"])
        self.headless_check.setChecked(CRAWLER_CONFIG["headless"])
        self.export_path_edit.setText(str(EXPORT_DIR))

    def save_settings(self):
        """保存设置"""
        # 更新配置
        CRAWLER_CONFIG["min_delay"] = self.min_delay_spin.value()
        CRAWLER_CONFIG["max_delay"] = self.max_delay_spin.value()
        CRAWLER_CONFIG["timeout"] = self.timeout_spin.value()
        CRAWLER_CONFIG["headless"] = self.headless_check.isChecked()

        # 保存到文件
        settings = {
            "crawler": {
                "min_delay": self.min_delay_spin.value(),
                "max_delay": self.max_delay_spin.value(),
                "timeout": self.timeout_spin.value(),
                "headless": self.headless_check.isChecked(),
            },
            "export": {
                "default_format": "excel",
            }
        }
        save_settings(settings)

        QMessageBox.information(self, "成功", "设置已保存！")
        self.accept()

    def browse_export_path(self):
        """浏览导出路径"""
        path = QFileDialog.getExistingDirectory(self, "选择导出路径", str(EXPORT_DIR))
        if path:
            self.export_path_edit.setText(path)
