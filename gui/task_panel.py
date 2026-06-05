"""
任务管理面板
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QProgressBar,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt, pyqtSignal


class TaskPanel(QWidget):
    """任务管理面板"""

    # 信号
    task_selected = pyqtSignal(int)  # 任务选中信号

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("任务列表")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFixedWidth(80)
        title_layout.addWidget(self.refresh_btn)

        layout.addLayout(title_layout)

        # 任务表格
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(5)
        self.task_table.setHorizontalHeaderLabels([
            "任务ID", "关键词", "平台", "状态", "评论数"
        ])

        header = self.task_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.task_table.setColumnWidth(0, 80)
        self.task_table.setColumnWidth(1, 200)
        self.task_table.setColumnWidth(2, 200)
        self.task_table.setColumnWidth(3, 100)

        self.task_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.task_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.task_table)

        # 进度区域
        progress_group = QWidget()
        progress_layout = QVBoxLayout(progress_group)

        self.progress_label = QLabel("准备就绪")
        progress_layout.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)

        self.detail_label = QLabel("")
        self.detail_label.setStyleSheet("color: #757575;")
        progress_layout.addWidget(self.detail_label)

        layout.addWidget(progress_group)

    def add_task(self, task_id: int, keyword: str, platforms: str):
        """添加任务到列表"""
        row = self.task_table.rowCount()
        self.task_table.insertRow(row)

        self.task_table.setItem(row, 0, QTableWidgetItem(str(task_id)))
        self.task_table.setItem(row, 1, QTableWidgetItem(keyword))
        self.task_table.setItem(row, 2, QTableWidgetItem(platforms))
        self.task_table.setItem(row, 3, QTableWidgetItem("进行中"))
        self.task_table.setItem(row, 4, QTableWidgetItem("0"))

    def update_task_status(self, task_id: int, status: str, comment_count: int = None):
        """更新任务状态"""
        for row in range(self.task_table.rowCount()):
            if self.task_table.item(row, 0).text() == str(task_id):
                self.task_table.setItem(row, 3, QTableWidgetItem(status))
                if comment_count is not None:
                    self.task_table.setItem(row, 4, QTableWidgetItem(str(comment_count)))
                break

    def update_progress(self, current: int, total: int, detail: str = ""):
        """更新进度"""
        if total > 0:
            percent = int(current / total * 100)
            self.progress_bar.setValue(percent)
            self.progress_label.setText(f"进度: {current}/{total} ({percent}%)")
        else:
            self.progress_bar.setValue(0)
            self.progress_label.setText("准备就绪")

        if detail:
            self.detail_label.setText(detail)

    def set_running(self, is_running: bool):
        """设置运行状态"""
        self.task_table.setEnabled(not is_running)
