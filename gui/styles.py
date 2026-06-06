"""
GUI 样式定义 - 增强版
"""

# 主题颜色
COLORS = {
    "primary": "#2196F3",       # 主色调（蓝色）
    "primary_dark": "#1976D2",  # 深蓝
    "primary_light": "#BBDEFB", # 浅蓝
    "accent": "#FF5722",        # 强调色（橙色）
    "success": "#4CAF50",       # 成功（绿色）
    "warning": "#FF9800",       # 警告（橙色）
    "danger": "#F44336",        # 危险（红色）
    "background": "#F5F5F5",    # 背景色
    "surface": "#FFFFFF",       # 表面色
    "text_primary": "#212121",  # 主要文字
    "text_secondary": "#757575",# 次要文字
    "border": "#E0E0E0",        # 边框色
    "highlight": "#E3F2FD",     # 高亮色
}

# 意向度颜色
INTENT_COLORS = {
    "高": "#F44336",  # 红色
    "中": "#FF9800",  # 橙色
    "低": "#9E9E9E",  # 灰色
}

# 全局样式表
STYLESHEET = f"""
/* 主窗口 */
QMainWindow {{
    background-color: {COLORS["background"]};
}}

/* 菜单栏 */
QMenuBar {{
    background-color: {COLORS["surface"]};
    border-bottom: 1px solid {COLORS["border"]};
    padding: 4px;
}}
QMenuBar::item:selected {{
    background-color: {COLORS["primary"]};
    color: white;
    border-radius: 4px;
}}

/* 按钮 */
QPushButton {{
    background-color: {COLORS["primary"]};
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    font-weight: bold;
}}
QPushButton:hover {{
    background-color: {COLORS["primary_dark"]};
}}
QPushButton:pressed {{
    background-color: #0D47A1;
}}
QPushButton:disabled {{
    background-color: #BDBDBD;
}}

/* 输入框 */
QLineEdit, QTextEdit, QSpinBox, QComboBox {{
    padding: 8px;
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    background-color: {COLORS["surface"]};
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {COLORS["primary"]};
}}

/* 表格 */
QTableWidget {{
    background-color: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    gridline-color: {COLORS["border"]};
}}
QTableWidget::item {{
    padding: 8px;
}}
QTableWidget::item:selected {{
    background-color: {COLORS["primary"]};
    color: white;
}}
QHeaderView::section {{
    background-color: {COLORS["primary"]};
    color: white;
    padding: 8px;
    border: none;
    font-weight: bold;
}}

/* 标签 */
QLabel {{
    color: {COLORS["text_primary"]};
}}

/* 分组框 */
QGroupBox {{
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}}

/* 状态栏 */
QStatusBar {{
    background-color: {COLORS["surface"]};
    border-top: 1px solid {COLORS["border"]};
    color: {COLORS["text_secondary"]};
}}

/* 复选框 */
QCheckBox {{
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
}}

/* 进度条 */
QProgressBar {{
    border: 1px solid {COLORS["border"]};
    border-radius: 4px;
    text-align: center;
    height: 20px;
}}
QProgressBar::chunk {{
    background-color: {COLORS["primary"]};
    border-radius: 3px;
}}

/* 标签页 */
QTabWidget::pane {{
    border: 1px solid {COLORS["border"]};
    background-color: {COLORS["surface"]};
}}
QTabBar::tab {{
    background-color: {COLORS["background"]};
    border: 1px solid {COLORS["border"]};
    padding: 8px 16px;
    margin-right: 2px;
}}
QTabBar::tab:selected {{
    background-color: {COLORS["surface"]};
    border-bottom-color: {COLORS["surface"]};
}}

/* 工具提示 */
QToolTip {{
    background-color: {COLORS["surface"]};
    color: {COLORS["text_primary"]};
    border: 1px solid {COLORS["border"]};
    padding: 4px;
}}

/* 滚动条 */
QScrollBar:vertical {{
    background-color: {COLORS["background"]};
    width: 12px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background-color: {COLORS["border"]};
    min-height: 20px;
    border-radius: 6px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {COLORS["text_secondary"]};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}

QScrollBar:horizontal {{
    background-color: {COLORS["background"]};
    height: 12px;
    margin: 0;
}}
QScrollBar::handle:horizontal {{
    background-color: {COLORS["border"]};
    min-width: 20px;
    border-radius: 6px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS["text_secondary"]};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
"""


def get_intent_style(intent: str) -> str:
    """获取意向度单元格样式"""
    color = INTENT_COLORS.get(intent, COLORS["text_secondary"])
    return f"color: {color}; font-weight: bold;"
