"""
结果表格 - 增强版，支持搜索和高级筛选
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QComboBox,
    QHeaderView, QAbstractItemView, QMenu, QApplication,
    QLineEdit, QGroupBox, QGridLayout, QCheckBox
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
        ("email", "邮箱", 150),
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

        # 搜索栏
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("搜索:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入关键词搜索评论内容、作者、联系方式...")
        self.search_input.textChanged.connect(self.apply_filter)
        search_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("搜索")
        self.search_btn.clicked.connect(self.apply_filter)
        search_layout.addWidget(self.search_btn)

        layout.addLayout(search_layout)

        # 筛选栏
        filter_layout = QHBoxLayout()

        # 统计标签
        self.stats_label = QLabel("共 0 条数据")
        filter_layout.addWidget(self.stats_label)

        filter_layout.addStretch()

        # 意向度筛选
        filter_layout.addWidget(QLabel("意向度:"))
        self.intent_filter = QComboBox()
        self.intent_filter.addItems(["全部", "高", "中", "低"])
        self.intent_filter.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.intent_filter)

        # 平台筛选
        filter_layout.addWidget(QLabel("平台:"))
        self.platform_filter = QComboBox()
        self.platform_filter.addItems(["全部", "抖音", "小红书", "快手", "B站", "微博", "知乎"])
        self.platform_filter.currentTextChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.platform_filter)

        # 联系方式筛选
        self.contact_only = QCheckBox("仅有联系方式")
        self.contact_only.stateChanged.connect(self.apply_filter)
        filter_layout.addWidget(self.contact_only)

        layout.addLayout(filter_layout)

        # 导出按钮
        export_layout = QHBoxLayout()

        self.export_excel_btn = QPushButton("导出 Excel")
        self.export_excel_btn.setStyleSheet("background-color: #4CAF50;")
        export_layout.addWidget(self.export_excel_btn)

        self.export_contacts_btn = QPushButton("导出联系方式")
        self.export_contacts_btn.setStyleSheet("background-color: #FF9800;")
        export_layout.addWidget(self.export_contacts_btn)

        self.export_high_intent_btn = QPushButton("导出高意向")
        self.export_high_intent_btn.setStyleSheet("background-color: #F44336;")
        export_layout.addWidget(self.export_high_intent_btn)

        export_layout.addStretch()

        layout.addLayout(export_layout)

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
        search_text = self.search_input.text().strip().lower()
        contact_only = self.contact_only.isChecked()

        filtered = self.all_data

        # 意向度筛选
        if intent_filter != "全部":
            filtered = [d for d in filtered if d.get("intent") == intent_filter]

        # 平台筛选
        if platform_filter != "全部":
            filtered = [d for d in filtered if d.get("platform") == platform_filter]

        # 仅有联系方式筛选
        if contact_only:
            filtered = [
                d for d in filtered
                if d.get("phone") or d.get("wechat") or d.get("qq") or d.get("email")
            ]

        # 关键词搜索
        if search_text:
            filtered = [
                d for d in filtered
                if search_text in str(d.get("content", "")).lower()
                or search_text in str(d.get("author", "")).lower()
                or search_text in str(d.get("phone", "")).lower()
                or search_text in str(d.get("wechat", "")).lower()
                or search_text in str(d.get("qq", "")).lower()
                or search_text in str(d.get("email", "")).lower()
                or search_text in str(d.get("title", "")).lower()
            ]

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
            if d.get("phone") or d.get("wechat") or d.get("qq") or d.get("email")
        ]
