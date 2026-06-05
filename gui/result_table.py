"""
结果表格
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QComboBox,
    QHeaderView, QAbstractItemView, QMenu, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QAction
from gui.styles import INTENT_COLORS


class ResultTable(QWidget):
    """结果表格组件"""

    # 列定义
    COLUMNS = [
        ("platform", "平台", 80),
        ("title", "视频标题", 200),
        ("content", "评论内容", 300),
        ("author", "客户昵称", 120),
        ("phone", "手机号", 120),
        ("wechat", "微信号", 120),
        ("qq", "QQ号", 100),
        ("intent", "意向度", 80),
        ("time", "时间", 120),
        ("url", "链接", 150),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # 工具栏
        toolbar_layout = QHBoxLayout()

        # 统计标签
        self.stats_label = QLabel("共 0 条数据")
        toolbar_layout.addWidget(self.stats_label)

        toolbar_layout.addStretch()

        # 筛选
        toolbar_layout.addWidget(QLabel("意向度:"))
        self.intent_filter = QComboBox()
        self.intent_filter.addItems(["全部", "高", "中", "低"])
        self.intent_filter.currentTextChanged.connect(self.apply_filter)
        toolbar_layout.addWidget(self.intent_filter)

        toolbar_layout.addWidget(QLabel("平台:"))
        self.platform_filter = QComboBox()
        self.platform_filter.addItems(["全部", "抖音", "小红书", "快手"])
        self.platform_filter.currentTextChanged.connect(self.apply_filter)
        toolbar_layout.addWidget(self.platform_filter)

        # 导出按钮
        self.export_excel_btn = QPushButton("导出 Excel")
        self.export_excel_btn.setStyleSheet("background-color: #4CAF50;")
        toolbar_layout.addWidget(self.export_excel_btn)

        self.export_contacts_btn = QPushButton("导出联系方式")
        self.export_contacts_btn.setStyleSheet("background-color: #FF9800;")
        toolbar_layout.addWidget(self.export_contacts_btn)

        layout.addLayout(toolbar_layout)

        # 表格
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.COLUMNS))
        self.table.setHorizontalHeaderLabels([col[1] for col in self.COLUMNS])

        # 设置列宽
        header = self.table.horizontalHeader()
        for i, (_, _, width) in enumerate(self.COLUMNS):
            self.table.setColumnWidth(i, width)
        header.setStretchLastSection(True)

        # 表格设置
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.show_context_menu)

        layout.addWidget(self.table)

        # 存储所有数据
        self.all_data = []

    def load_data(self, data: list):
        """加载数据到表格"""
        self.all_data = data
        self.update_table(data)

    def update_table(self, data: list):
        """更新表格显示"""
        self.table.setRowCount(len(data))

        for row_idx, row_data in enumerate(data):
            for col_idx, (key, _, _) in enumerate(self.COLUMNS):
                value = str(row_data.get(key, ""))
                item = QTableWidgetItem(value)

                # 意向度颜色
                if key == "intent":
                    color = INTENT_COLORS.get(value, "#9E9E9E")
                    item.setForeground(QColor(color))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                # 链接列可点击
                if key == "url" and value:
                    item.setForeground(QColor("#2196F3"))

                self.table.setItem(row_idx, col_idx, item)

        # 更新统计
        self.stats_label.setText(f"共 {len(data)} 条数据")

    def apply_filter(self):
        """应用筛选"""
        intent_filter = self.intent_filter.currentText()
        platform_filter = self.platform_filter.currentText()

        filtered = self.all_data

        if intent_filter != "全部":
            filtered = [d for d in filtered if d.get("intent") == intent_filter]

        if platform_filter != "全部":
            filtered = [d for d in filtered if d.get("platform") == platform_filter]

        self.update_table(filtered)

    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)

        copy_action = QAction("复制选中行", self)
        copy_action.triggered.connect(self.copy_selected)
        menu.addAction(copy_action)

        copy_phone_action = QAction("复制所有手机号", self)
        copy_phone_action.triggered.connect(self.copy_all_phones)
        menu.addAction(copy_phone_action)

        copy_wechat_action = QAction("复制所有微信号", self)
        copy_wechat_action.triggered.connect(self.copy_all_wechats)
        menu.addAction(copy_wechat_action)

        menu.exec(self.table.mapToGlobal(pos))

    def copy_selected(self):
        """复制选中行"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            return

        texts = []
        for row in sorted(selected_rows):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            texts.append("\t".join(row_data))

        QApplication.clipboard().setText("\n".join(texts))

    def copy_all_phones(self):
        """复制所有手机号"""
        phones = []
        for row in range(self.table.rowCount()):
            phone_item = self.table.item(row, 4)  # 手机号列
            if phone_item and phone_item.text():
                phones.append(phone_item.text())

        if phones:
            QApplication.clipboard().setText("\n".join(phones))

    def copy_all_wechats(self):
        """复制所有微信号"""
        wechats = []
        for row in range(self.table.rowCount()):
            wechat_item = self.table.item(row, 5)  # 微信号列
            if wechat_item and wechat_item.text():
                wechats.append(wechat_item.text())

        if wechats:
            QApplication.clipboard().setText("\n".join(wechats))

    def get_filtered_data(self) -> list:
        """获取当前筛选后的数据"""
        intent_filter = self.intent_filter.currentText()
        platform_filter = self.platform_filter.currentText()

        filtered = self.all_data

        if intent_filter != "全部":
            filtered = [d for d in filtered if d.get("intent") == intent_filter]

        if platform_filter != "全部":
            filtered = [d for d in filtered if d.get("platform") == platform_filter]

        return filtered

    def get_contacts_data(self) -> list:
        """获取包含联系方式的数据"""
        return [
            d for d in self.all_data
            if d.get("phone") or d.get("wechat") or d.get("qq")
        ]
