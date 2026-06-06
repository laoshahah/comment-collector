"""
数据仪表盘 - 显示统计图表
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QGroupBox, QGridLayout, QFrame
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPainter, QPen, QBrush
from storage.database import Database
from utils.logger import logger


class StatCard(QFrame):
    """统计卡片"""

    def __init__(self, title: str, value: str = "0", color: str = "#2196F3", parent=None):
        super().__init__(parent)
        self.title = title
        self.value = value
        self.color = color
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {self.color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)

        layout = QVBoxLayout(self)

        # 标题
        title_label = QLabel(self.title)
        title_label.setStyleSheet(f"color: {self.color}; font-size: 14px; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # 数值
        self.value_label = QLabel(self.value)
        self.value_label.setStyleSheet(f"color: #333; font-size: 24px; font-weight: bold;")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.value_label)

    def update_value(self, value: str):
        """更新数值"""
        self.value = value
        self.value_label.setText(value)


class PieChartWidget(QWidget):
    """饼图组件"""

    def __init__(self, title: str, data: dict = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.data = data or {}
        self.colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]
        self.setMinimumSize(200, 200)

    def set_data(self, data: dict):
        """设置数据"""
        self.data = data
        self.update()

    def paintEvent(self, event):
        """绘制饼图"""
        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 计算区域
        width = self.width()
        height = self.height()
        size = min(width, height) - 60
        x = (width - size) // 2
        y = 30

        # 绘制标题
        painter.setPen(QPen(QColor("#333")))
        painter.setFont(painter.font())
        painter.drawText(0, 0, width, 30, Qt.AlignmentFlag.AlignCenter, self.title)

        # 计算总数
        total = sum(self.data.values())
        if total == 0:
            painter.end()
            return

        # 绘制饼图
        start_angle = 0
        legend_y = y + size + 10

        for i, (label, value) in enumerate(self.data.items()):
            if value == 0:
                continue

            # 计算角度
            angle = int(360 * 16 * value / total)
            color = QColor(self.colors[i % len(self.colors)])

            # 绘制扇形
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.drawPie(x, y, size, size, start_angle, angle)

            # 绘制图例
            legend_x = 10
            painter.setBrush(QBrush(color))
            painter.drawRect(legend_x, legend_y, 12, 12)
            painter.setPen(QPen(QColor("#333")))
            painter.drawText(legend_x + 16, legend_y, 100, 16, Qt.AlignmentFlag.AlignLeft, f"{label}: {value}")

            legend_y += 20
            start_angle += angle

        painter.end()


class BarChartWidget(QWidget):
    """柱状图组件"""

    def __init__(self, title: str, data: dict = None, parent=None):
        super().__init__(parent)
        self.title = title
        self.data = data or {}
        self.colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF", "#FF9F40"]
        self.setMinimumSize(200, 200)

    def set_data(self, data: dict):
        """设置数据"""
        self.data = data
        self.update()

    def paintEvent(self, event):
        """绘制柱状图"""
        if not self.data:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 计算区域
        width = self.width()
        height = self.height()

        # 绘制标题
        painter.setPen(QPen(QColor("#333")))
        painter.drawText(0, 0, width, 30, Qt.AlignmentFlag.AlignCenter, self.title)

        if not self.data:
            painter.end()
            return

        # 计算柱状图参数
        max_value = max(self.data.values()) if self.data else 1
        bar_count = len(self.data)
        bar_width = min(60, (width - 40) // bar_count)
        chart_height = height - 80
        chart_y = 30

        # 绘制柱子
        x = 20
        for i, (label, value) in enumerate(self.data.items()):
            color = QColor(self.colors[i % len(self.colors)])
            bar_height = int(chart_height * value / max_value) if max_value > 0 else 0

            # 绘制柱子
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(Qt.GlobalColor.white, 1))
            painter.drawRect(x, chart_y + chart_height - bar_height, bar_width, bar_height)

            # 绘制数值
            painter.setPen(QPen(QColor("#333")))
            painter.drawText(x, chart_y + chart_height - bar_height - 20, bar_width, 20,
                           Qt.AlignmentFlag.AlignCenter, str(value))

            # 绘制标签
            painter.drawText(x, chart_y + chart_height + 5, bar_width, 20,
                           Qt.AlignmentFlag.AlignCenter, label)

            x += bar_width + 10

        painter.end()


class DashboardTab(QWidget):
    """数据仪表盘"""

    def __init__(self, db: Database, parent=None):
        super().__init__(parent)
        self.db = db
        self.init_ui()
        self.refresh_data()

    def init_ui(self):
        """初始化界面"""
        layout = QVBoxLayout(self)

        # 统计卡片区域
        cards_group = QGroupBox("数据概览")
        cards_layout = QGridLayout(cards_group)

        # 创建统计卡片
        self.total_card = StatCard("总评论数", "0", "#2196F3")
        self.contact_card = StatCard("有联系方式", "0", "#4CAF50")
        self.high_intent_card = StatCard("高意向客户", "0", "#FF5722")
        self.phone_card = StatCard("手机号", "0", "#9C27B0")
        self.wechat_card = StatCard("微信号", "0", "#FF9800")
        self.email_card = StatCard("邮箱", "0", "#607D8B")

        cards_layout.addWidget(self.total_card, 0, 0)
        cards_layout.addWidget(self.contact_card, 0, 1)
        cards_layout.addWidget(self.high_intent_card, 0, 2)
        cards_layout.addWidget(self.phone_card, 1, 0)
        cards_layout.addWidget(self.wechat_card, 1, 1)
        cards_layout.addWidget(self.email_card, 1, 2)

        layout.addWidget(cards_group)

        # 图表区域
        charts_layout = QHBoxLayout()

        # 平台分布饼图
        self.platform_chart = PieChartWidget("平台分布")
        charts_layout.addWidget(self.platform_chart)

        # 意向度分布饼图
        self.intent_chart = PieChartWidget("意向度分布")
        charts_layout.addWidget(self.intent_chart)

        # 联系方式对比柱状图
        self.contact_chart = BarChartWidget("联系方式统计")
        charts_layout.addWidget(self.contact_chart)

        layout.addLayout(charts_layout)

        # 刷新按钮
        refresh_btn = QHBoxLayout()
        refresh_btn.addStretch()

        from PyQt6.QtWidgets import QPushButton
        refresh_button = QPushButton("刷新数据")
        refresh_button.clicked.connect(self.refresh_data)
        refresh_btn.addWidget(refresh_button)

        layout.addLayout(refresh_btn)

    def refresh_data(self):
        """刷新数据"""
        try:
            stats = self.db.get_statistics()

            # 更新统计卡片
            self.total_card.update_value(str(stats.get("total", 0)))
            self.contact_card.update_value(str(stats.get("with_contact", 0)))
            self.high_intent_card.update_value(str(stats.get("intents", {}).get("高", 0)))
            self.phone_card.update_value(str(stats.get("with_phone", 0)))
            self.wechat_card.update_value(str(stats.get("with_wechat", 0)))
            self.email_card.update_value(str(stats.get("with_email", 0)))

            # 更新图表
            self.platform_chart.set_data(stats.get("platforms", {}))
            self.intent_chart.set_data(stats.get("intents", {}))

            contact_data = {
                "手机号": stats.get("with_phone", 0),
                "微信": stats.get("with_wechat", 0),
                "QQ": stats.get("with_qq", 0),
                "邮箱": stats.get("with_email", 0),
            }
            self.contact_chart.set_data(contact_data)

            logger.info("仪表盘数据已刷新")

        except Exception as e:
            logger.error(f"刷新仪表盘数据失败: {e}")
