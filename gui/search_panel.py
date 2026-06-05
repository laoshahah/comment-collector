"""
搜索面板
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QCheckBox,
    QGroupBox, QSpinBox, QGridLayout
)
from PyQt6.QtCore import pyqtSignal
from config import PLATFORMS


class SearchPanel(QWidget):
    """搜索面板"""

    # 信号
    search_started = pyqtSignal(dict)  # 搜索开始信号，传递搜索参数

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # 搜索条件组
        search_group = QGroupBox("搜索条件")
        search_layout = QGridLayout(search_group)

        # 关键词输入
        search_layout.addWidget(QLabel("关键词:"), 0, 0)
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入搜索关键词，如：产品名、品牌词、痛点词")
        search_layout.addWidget(self.keyword_input, 0, 1, 1, 3)

        # 平台选择
        search_layout.addWidget(QLabel("平台:"), 1, 0)
        platform_layout = QHBoxLayout()
        self.platform_checks = {}
        for key, info in PLATFORMS.items():
            if info["enabled"]:
                cb = QCheckBox(info["name"])
                cb.setChecked(True)
                self.platform_checks[key] = cb
                platform_layout.addWidget(cb)
        platform_layout.addStretch()
        search_layout.addLayout(platform_layout, 1, 1, 1, 3)

        # 爬取设置
        search_layout.addWidget(QLabel("最大页数:"), 2, 0)
        self.max_pages_spin = QSpinBox()
        self.max_pages_spin.setRange(1, 50)
        self.max_pages_spin.setValue(5)
        search_layout.addWidget(self.max_pages_spin, 2, 1)

        search_layout.addWidget(QLabel("每页评论:"), 2, 2)
        self.max_comments_spin = QSpinBox()
        self.max_comments_spin.setRange(10, 500)
        self.max_comments_spin.setValue(50)
        self.max_comments_spin.setSingleStep(10)
        search_layout.addWidget(self.max_comments_spin, 2, 3)

        layout.addWidget(search_group)

        # 按钮区域
        btn_layout = QHBoxLayout()

        self.search_btn = QPushButton("开始搜索")
        self.search_btn.setFixedHeight(40)
        self.search_btn.clicked.connect(self.on_search)
        btn_layout.addWidget(self.search_btn)

        self.stop_btn = QPushButton("停止")
        self.stop_btn.setFixedHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #F44336;")
        btn_layout.addWidget(self.stop_btn)

        btn_layout.addStretch()

        self.clear_btn = QPushButton("清空条件")
        self.clear_btn.setFixedHeight(40)
        self.clear_btn.setStyleSheet("background-color: #757575;")
        self.clear_btn.clicked.connect(self.on_clear)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def on_search(self):
        """开始搜索"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            return

        # 获取选中的平台
        selected_platforms = [
            key for key, cb in self.platform_checks.items()
            if cb.isChecked()
        ]

        if not selected_platforms:
            return

        params = {
            "keyword": keyword,
            "platforms": selected_platforms,
            "max_pages": self.max_pages_spin.value(),
            "max_comments": self.max_comments_spin.value(),
        }

        self.search_started.emit(params)

    def on_clear(self):
        """清空搜索条件"""
        self.keyword_input.clear()
        for cb in self.platform_checks.values():
            cb.setChecked(True)
        self.max_pages_spin.setValue(5)
        self.max_comments_spin.setValue(50)

    def set_searching(self, is_searching: bool):
        """设置搜索状态"""
        self.search_btn.setEnabled(not is_searching)
        self.stop_btn.setEnabled(is_searching)
        self.keyword_input.setEnabled(not is_searching)
