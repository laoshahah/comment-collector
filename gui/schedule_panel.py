"""
定时任务管理面板
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QComboBox,
    QHeaderView, QAbstractItemView, QTimeEdit, QLineEdit,
    QCheckBox, QDialog, QFormLayout, QMessageBox, QGroupBox
)
from PyQt6.QtCore import Qt, QTime, pyqtSignal
from utils.scheduler import TaskScheduler, ScheduledTask
from config import PLATFORMS
from utils.logger import logger


class AddTaskDialog(QDialog):
    """添加定时任务对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加定时任务")
        self.setMinimumWidth(400)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QFormLayout(self)

        # 关键词
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("输入搜索关键词")
        layout.addRow("关键词:", self.keyword_input)

        # 平台选择
        platform_group = QGroupBox("选择平台")
        platform_layout = QVBoxLayout(platform_group)
        self.platform_checks = {}
        for key, info in PLATFORMS.items():
            if info["enabled"]:
                cb = QCheckBox(info["name"])
                cb.setChecked(True)
                self.platform_checks[key] = cb
                platform_layout.addWidget(cb)
        layout.addRow(platform_group)

        # 定时类型
        self.schedule_type = QComboBox()
        self.schedule_type.addItems(["每天", "每小时", "每周"])
        layout.addRow("执行频率:", self.schedule_type)

        # 执行时间
        self.schedule_time = QTimeEdit()
        self.schedule_time.setDisplayFormat("HH:mm")
        self.schedule_time.setTime(QTime(9, 0))
        layout.addRow("执行时间:", self.schedule_time)

        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self.accept)
        btn_layout.addWidget(save_btn)

        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("background-color: #757575;")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        layout.addRow(btn_layout)

    def get_data(self) -> dict:
        """获取表单数据"""
        keyword = self.keyword_input.text().strip()
        platforms = [key for key, cb in self.platform_checks.items() if cb.isChecked()]

        schedule_type_map = {"每天": "daily", "每小时": "hourly", "每周": "weekly"}
        schedule_type = schedule_type_map[self.schedule_type.currentText()]

        schedule_time = self.schedule_time.time().toString("HH:mm")

        return {
            "keyword": keyword,
            "platforms": platforms,
            "schedule_type": schedule_type,
            "schedule_time": schedule_time,
        }


class SchedulePanel(QWidget):
    """定时任务管理面板"""

    # 信号
    task_added = pyqtSignal(dict)  # 任务添加信号

    def __init__(self, scheduler: TaskScheduler, parent=None):
        super().__init__(parent)
        self.scheduler = scheduler
        self.init_ui()
        self.refresh_tasks()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 标题
        title_layout = QHBoxLayout()
        title_label = QLabel("定时任务管理")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()

        # 添加任务按钮
        add_btn = QPushButton("添加任务")
        add_btn.setStyleSheet("background-color: #4CAF50;")
        add_btn.clicked.connect(self.add_task)
        title_layout.addWidget(add_btn)

        layout.addLayout(title_layout)

        # 任务表格
        self.task_table = QTableWidget()
        self.task_table.setColumnCount(6)
        self.task_table.setHorizontalHeaderLabels([
            "ID", "关键词", "平台", "执行频率", "执行时间", "启用"
        ])

        header = self.task_table.horizontalHeader()
        header.setStretchLastSection(True)
        self.task_table.setColumnWidth(0, 50)
        self.task_table.setColumnWidth(1, 150)
        self.task_table.setColumnWidth(2, 200)
        self.task_table.setColumnWidth(3, 100)
        self.task_table.setColumnWidth(4, 100)

        self.task_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.task_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        layout.addWidget(self.task_table)

        # 按钮区域
        btn_layout = QHBoxLayout()

        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self.refresh_tasks)
        btn_layout.addWidget(refresh_btn)

        delete_btn = QPushButton("删除选中")
        delete_btn.setStyleSheet("background-color: #F44336;")
        delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(delete_btn)

        btn_layout.addStretch()

        layout.addLayout(btn_layout)

    def add_task(self):
        """添加任务"""
        dialog = AddTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            if data["keyword"] and data["platforms"]:
                task = self.scheduler.add_task(
                    keyword=data["keyword"],
                    platforms=data["platforms"],
                    schedule_type=data["schedule_type"],
                    schedule_time=data["schedule_time"],
                )
                self.refresh_tasks()
                self.task_added.emit(data)
                QMessageBox.information(self, "成功", f"定时任务已添加: {data['keyword']}")
            else:
                QMessageBox.warning(self, "提示", "请填写关键词并选择平台")

    def refresh_tasks(self):
        """刷新任务列表"""
        tasks = self.scheduler.get_tasks()
        self.task_table.setRowCount(len(tasks))

        for row, task in enumerate(tasks):
            self.task_table.setItem(row, 0, QTableWidgetItem(str(task.task_id)))
            self.task_table.setItem(row, 1, QTableWidgetItem(task.keyword))

            # 平台名称
            platform_names = {
                "douyin": "抖音", "xiaohongshu": "小红书", "kuaishou": "快手",
                "bilibili": "B站", "weibo": "微博", "zhihu": "知乎"
            }
            platforms_str = ", ".join(platform_names.get(p, p) for p in task.platforms)
            self.task_table.setItem(row, 2, QTableWidgetItem(platforms_str))

            # 执行频率
            type_names = {"daily": "每天", "hourly": "每小时", "weekly": "每周"}
            self.task_table.setItem(row, 3, QTableWidgetItem(type_names.get(task.schedule_type, task.schedule_type)))

            # 执行时间
            self.task_table.setItem(row, 4, QTableWidgetItem(task.schedule_time))

            # 启用状态
            check = QCheckBox()
            check.setChecked(task.enabled)
            check.stateChanged.connect(lambda state, tid=task.task_id: self.toggle_task(tid, state))
            self.task_table.setCellWidget(row, 5, check)

    def toggle_task(self, task_id: int, state: int):
        """切换任务启用状态"""
        enabled = state == Qt.CheckState.Checked.value
        self.scheduler.update_task(task_id, enabled=enabled)
        logger.info(f"任务 {task_id} {'启用' if enabled else '禁用'}")

    def delete_selected(self):
        """删除选中的任务"""
        selected_rows = set()
        for item in self.task_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.warning(self, "提示", "请先选择要删除的任务")
            return

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除选中的 {len(selected_rows)} 个任务吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            for row in sorted(selected_rows, reverse=True):
                task_id = int(self.task_table.item(row, 0).text())
                self.scheduler.remove_task(task_id)

            self.refresh_tasks()
            QMessageBox.information(self, "成功", "任务已删除")
