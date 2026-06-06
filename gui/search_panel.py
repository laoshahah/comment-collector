"""
搜索面板
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QCheckBox,
    QGroupBox, QSpinBox, QGridLayout, QMenu,
    QMessageBox, QInputDialog, QFileDialog
)
from PyQt6.QtCore import pyqtSignal
from config import PLATFORMS


class SearchPanel(QWidget):
    """搜索面板"""

    # 信号
    search_started = pyqtSignal(dict)  # 搜索开始信号，传递搜索参数
    bulk_import = pyqtSignal(list)  # 批量导入URL信号

    def __init__(self, db=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # 搜索条件组
        search_group = QGroupBox("搜索条件")
        search_layout = QGridLayout(search_group)

        # 关键词输入（带历史记录）
        search_layout.addWidget(QLabel("关键词:"), 0, 0)
        keyword_layout = QHBoxLayout()
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入搜索关键词，如：产品名、品牌词、痛点词")
        keyword_layout.addWidget(self.keyword_input)

        # 历史记录按钮
        self.history_btn = QPushButton("历史")
        self.history_btn.setFixedWidth(60)
        self.history_btn.clicked.connect(self.show_history_menu)
        keyword_layout.addWidget(self.history_btn)

        search_layout.addLayout(keyword_layout, 0, 1, 1, 3)

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

        # 批量导入按钮
        self.bulk_btn = QPushButton("批量导入URL")
        self.bulk_btn.setFixedHeight(40)
        self.bulk_btn.setStyleSheet("background-color: #FF9800;")
        self.bulk_btn.clicked.connect(self.on_bulk_import)
        btn_layout.addWidget(self.bulk_btn)

        btn_layout.addStretch()

        self.clear_btn = QPushButton("清空条件")
        self.clear_btn.setFixedHeight(40)
        self.clear_btn.setStyleSheet("background-color: #757575;")
        self.clear_btn.clicked.connect(self.on_clear)
        btn_layout.addWidget(self.clear_btn)

        layout.addLayout(btn_layout)
        layout.addStretch()

    def show_history_menu(self):
        """显示历史记录菜单"""
        if not self.db:
            return

        menu = QMenu(self)
        history = self.db.get_search_history(limit=10)

        if not history:
            menu.addAction("暂无历史记录").setEnabled(False)
        else:
            for item in history:
                action = menu.addAction(f"{item['keyword']} ({item['platforms']})")
                action.setData(item['keyword'])
                action.triggered.connect(lambda checked, kw=item['keyword']: self.keyword_input.setText(kw))

            menu.addSeparator()
            clear_action = menu.addAction("清空历史记录")
            clear_action.triggered.connect(self.clear_history)

        menu.exec(self.history_btn.mapToGlobal(self.history_btn.rect().bottomLeft()))

    def clear_history(self):
        """清空历史记录"""
        if self.db:
            reply = QMessageBox.question(
                self, "确认", "确定要清空所有搜索历史吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.db.clear_search_history()
                QMessageBox.information(self, "成功", "历史记录已清空")

    def on_search(self):
        """开始搜索"""
        keyword = self.keyword_input.text().strip()
        if not keyword:
            QMessageBox.warning(self, "提示", "请输入搜索关键词")
            return

        # 获取选中的平台
        selected_platforms = [
            key for key, cb in self.platform_checks.items()
            if cb.isChecked()
        ]

        if not selected_platforms:
            QMessageBox.warning(self, "提示", "请至少选择一个平台")
            return

        # 保存到搜索历史
        if self.db:
            platforms_str = ", ".join(selected_platforms)
            self.db.add_search_history(keyword, platforms_str)

        params = {
            "keyword": keyword,
            "platforms": selected_platforms,
            "max_pages": self.max_pages_spin.value(),
            "max_comments": self.max_comments_spin.value(),
        }

        self.search_started.emit(params)

    def on_bulk_import(self):
        """批量导入URL"""
        # 选择导入方式
        options = ["从文件导入", "手动输入"]
        choice, ok = QInputDialog.getItem(
            self, "批量导入", "选择导入方式:", options, 0, False
        )

        if not ok:
            return

        urls = []

        if choice == "从文件导入":
            # 从文件导入
            file_path, _ = QFileDialog.getOpenFileName(
                self, "选择文件", "", "文本文件 (*.txt);;CSV文件 (*.csv);;所有文件 (*)"
            )
            if file_path:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            url = line.strip()
                            if url and url.startswith('http'):
                                urls.append(url)
                except Exception as e:
                    QMessageBox.critical(self, "错误", f"读取文件失败: {e}")
                    return
        else:
            # 手动输入
            text, ok = QInputDialog.getMultiLineText(
                self, "批量导入", "请输入URL（每行一个）:", ""
            )
            if ok and text:
                for line in text.split('\n'):
                    url = line.strip()
                    if url and url.startswith('http'):
                        urls.append(url)

        if urls:
            # 保存到数据库
            if self.db:
                self.db.add_bulk_urls(urls)

            QMessageBox.information(
                self, "成功", f"已导入 {len(urls)} 个URL"
            )
            self.bulk_import.emit(urls)

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
        self.bulk_btn.setEnabled(not is_searching)
