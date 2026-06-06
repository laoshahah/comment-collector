"""
主窗口
"""
import asyncio
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QStatusBar, QMenuBar, QMenu, QMessageBox,
    QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction
from playwright.async_api import async_playwright

from gui.search_panel import SearchPanel
from gui.result_table import ResultTable
from gui.task_panel import TaskPanel
from gui.dashboard_tab import DashboardTab
from gui.schedule_panel import SchedulePanel
from gui.settings_dialog import SettingsDialog
from gui.update_dialog import UpdateDialog
from gui.styles import STYLESHEET
from config import __version__
from storage.database import Database
from storage.exporter import Exporter
from utils.scheduler import TaskScheduler
from utils.logger import logger


class CrawlerThread(QThread):
    """爬虫工作线程"""

    progress = pyqtSignal(int, int, str)  # current, total, detail
    finished = pyqtSignal(list)  # results
    error = pyqtSignal(str)  # error message

    def __init__(self, params: dict):
        super().__init__()
        self.params = params
        self.is_running = True

    def run(self):
        """执行爬虫任务"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            results = loop.run_until_complete(self._crawl())
            if self.is_running:
                self.finished.emit(results)
        except Exception as e:
            if self.is_running:
                self.error.emit(str(e))

    async def _crawl(self):
        """异步爬取"""
        from crawlers.douyin_crawler import DouyinCrawler
        from crawlers.xiaohongshu_crawler import XiaohongshuCrawler
        from crawlers.kuaishou_crawler import KuaishouCrawler
        from crawlers.bilibili_crawler import BilibiliCrawler
        from crawlers.weibo_crawler import WeiboCrawler
        from crawlers.zhihu_crawler import ZhihuCrawler
        from crawlers.simple_crawler import SimpleCrawler
        from config import PLATFORMS
        from parsers.comment_parser import CommentParser
        from parsers.info_extractor import InfoExtractor

        keyword = self.params["keyword"]
        platforms = self.params["platforms"]
        max_pages = self.params["max_pages"]
        max_comments = self.params["max_comments"]

        all_results = []
        total_platforms = len(platforms)

        # 平台爬虫映射
        crawler_map = {
            "douyin": DouyinCrawler,
            "xiaohongshu": XiaohongshuCrawler,
            "kuaishou": KuaishouCrawler,
            "bilibili": BilibiliCrawler,
            "weibo": WeiboCrawler,
            "zhihu": ZhihuCrawler,
        }

        async with async_playwright() as p:
            for idx, platform_key in enumerate(platforms):
                if not self.is_running:
                    break

                crawler_cls = crawler_map.get(platform_key)
                if not crawler_cls:
                    continue

                platform_name = {
                    "douyin": "抖音",
                    "xiaohongshu": "小红书",
                    "kuaishou": "快手",
                    "bilibili": "B站",
                    "weibo": "微博",
                    "zhihu": "知乎",
                }.get(platform_key, platform_key)

                self.progress.emit(idx, total_platforms, f"正在爬取 {platform_name}...")

                crawler = crawler_cls()
                try:
                    await crawler.init_browser(p)

                    # 搜索内容
                    self.progress.emit(idx, total_platforms, f"{platform_name}: 搜索中...")
                    contents = await crawler.search(keyword, max_pages)

                    # 如果主爬虫没有结果，使用简化爬虫
                    if not contents:
                        logger.info(f"{platform_name}: 主爬虫无结果，使用简化爬虫")
                        platform_config = PLATFORMS.get(platform_key, {})
                        search_url = platform_config.get("search_url", "")
                        if search_url:
                            simple_crawler = SimpleCrawler(platform_name, search_url)
                            await simple_crawler.init_browser(p)
                            simple_results = await simple_crawler.search(keyword, max_pages)
                            all_results.extend(simple_results)
                            await simple_crawler.close()
                        continue

                    # 爬取每个内容的评论
                    for content_idx, content in enumerate(contents[:10]):  # 限制前10个内容
                        if not self.is_running:
                            break

                        self.progress.emit(
                            idx, total_platforms,
                            f"{platform_name}: 爬取评论 {content_idx + 1}/{min(len(contents), 10)}"
                        )

                        comments = await crawler.get_comments(content["url"], max_comments)

                        # 过滤和去重
                        comments = CommentParser.filter_invalid_comments(comments)
                        comments = CommentParser.deduplicate_comments(comments)

                        # 提取客户信息
                        comments = InfoExtractor.process_comments(comments)

                        # 转换为字典
                        for comment in comments:
                            all_results.append({
                                "platform": comment.platform,
                                "title": comment.title,
                                "content": comment.content,
                                "author": comment.author,
                                "phone": comment.phone,
                                "wechat": comment.wechat,
                                "qq": comment.qq,
                                "email": comment.email,
                                "intent": comment.intent,
                                "time": comment.time,
                                "url": comment.url,
                                "likes": comment.likes,
                            })

                except Exception as e:
                    logger.error(f"{platform_name} 爬取失败: {e}")
                finally:
                    await crawler.close()

        return all_results

    def stop(self):
        """停止爬虫"""
        self.is_running = False


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.scheduler = TaskScheduler()
        self.crawler_thread = None
        self.current_task_id = None
        self.init_ui()
        self.load_history_data()
        # 启动定时任务调度器
        self.scheduler.start(self.on_scheduled_task)

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("跨平台评论采集与客户信息提取工具")
        self.setMinimumSize(1200, 800)

        # 应用样式
        self.setStyleSheet(STYLESHEET)

        # 创建菜单栏
        self.create_menu_bar()

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 标签页
        self.tab_widget = QTabWidget()

        # 搜索标签页
        search_tab = QWidget()
        search_layout = QVBoxLayout(search_tab)

        self.search_panel = SearchPanel(db=self.db)
        self.search_panel.search_started.connect(self.start_crawl)
        self.search_panel.stop_btn.clicked.connect(self.stop_crawl)
        self.search_panel.bulk_import.connect(self.on_bulk_import)
        search_layout.addWidget(self.search_panel)

        self.result_table = ResultTable()
        self.result_table.export_excel_btn.clicked.connect(self.export_excel)
        self.result_table.export_contacts_btn.clicked.connect(self.export_contacts)
        search_layout.addWidget(self.result_table)

        self.tab_widget.addTab(search_tab, "搜索采集")

        # 任务标签页
        self.task_panel = TaskPanel()
        self.tab_widget.addTab(self.task_panel, "任务管理")

        # 仪表盘标签页
        self.dashboard_tab = DashboardTab(self.db)
        self.tab_widget.addTab(self.dashboard_tab, "数据仪表盘")

        # 定时任务标签页
        self.schedule_panel = SchedulePanel(self.scheduler)
        self.tab_widget.addTab(self.schedule_panel, "定时任务")

        main_layout.addWidget(self.tab_widget)

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("准备就绪")

    def create_menu_bar(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu("文件")

        export_action = QAction("导出 Excel", self)
        export_action.triggered.connect(self.export_excel)
        file_menu.addAction(export_action)

        export_contacts_action = QAction("导出联系方式", self)
        export_contacts_action.triggered.connect(self.export_contacts)
        file_menu.addAction(export_contacts_action)

        file_menu.addSeparator()

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 设置菜单
        settings_menu = menubar.addMenu("设置")

        settings_action = QAction("偏好设置", self)
        settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(settings_action)

        # 帮助菜单
        help_menu = menubar.addMenu("帮助")

        update_action = QAction("检查更新", self)
        update_action.triggered.connect(self.check_update)
        help_menu.addAction(update_action)

        help_menu.addSeparator()

        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def start_crawl(self, params: dict):
        """开始爬取"""
        keyword = params["keyword"]
        platforms = params["platforms"]

        # 创建任务记录
        platform_names = {
            "douyin": "抖音",
            "xiaohongshu": "小红书",
            "kuaishou": "快手",
        }
        platforms_str = ", ".join(platform_names.get(p, p) for p in platforms)

        self.current_task_id = self.db.insert_task(keyword, platforms_str)
        self.task_panel.add_task(self.current_task_id, keyword, platforms_str)

        # 启动爬虫线程
        self.crawler_thread = CrawlerThread(params)
        self.crawler_thread.progress.connect(self.on_crawl_progress)
        self.crawler_thread.finished.connect(self.on_crawl_finished)
        self.crawler_thread.error.connect(self.on_crawl_error)

        self.search_panel.set_searching(True)
        self.task_panel.set_running(True)
        self.status_bar.showMessage("正在爬取...")

        self.crawler_thread.start()

    def stop_crawl(self):
        """停止爬取"""
        if self.crawler_thread:
            self.crawler_thread.stop()
            self.status_bar.showMessage("正在停止...")

    def on_crawl_progress(self, current: int, total: int, detail: str):
        """爬取进度更新"""
        self.task_panel.update_progress(current, total, detail)
        self.status_bar.showMessage(detail)

    def on_crawl_finished(self, results: list):
        """爬取完成"""
        # 保存到数据库
        saved_count = self.db.insert_comments_batch(results)

        # 更新表格
        self.result_table.load_data(results)

        # 更新任务状态
        if self.current_task_id:
            self.db.update_task_status(self.current_task_id, "completed", len(results))
            self.task_panel.update_task_status(self.current_task_id, "已完成", len(results))

        # 恢复界面状态
        self.search_panel.set_searching(False)
        self.task_panel.set_running(False)
        self.status_bar.showMessage(f"爬取完成: {len(results)} 条评论, 保存 {saved_count} 条")

        # 显示统计
        with_contact = sum(1 for r in results if r.get("phone") or r.get("wechat") or r.get("qq"))
        high_intent = sum(1 for r in results if r.get("intent") == "高")

        QMessageBox.information(
            self, "爬取完成",
            f"共采集 {len(results)} 条评论\n"
            f"有联系方式: {with_contact} 条\n"
            f"高意向客户: {high_intent} 条"
        )

    def on_crawl_error(self, error_msg: str):
        """爬取出错"""
        self.search_panel.set_searching(False)
        self.task_panel.set_running(False)
        self.status_bar.showMessage(f"爬取出错: {error_msg}")

        if self.current_task_id:
            self.db.update_task_status(self.current_task_id, "failed")
            self.task_panel.update_task_status(self.current_task_id, "失败")

        QMessageBox.critical(self, "错误", f"爬取失败: {error_msg}")

    def export_excel(self):
        """导出 Excel"""
        data = self.result_table.get_filtered_data()
        if not data:
            QMessageBox.warning(self, "提示", "没有数据可导出")
            return

        filepath = Exporter.export_excel(data)
        if filepath:
            QMessageBox.information(self, "导出成功", f"已导出到: {filepath}")

    def export_contacts(self):
        """导出联系方式"""
        data = self.result_table.get_contacts_data()
        if not data:
            QMessageBox.warning(self, "提示", "没有包含联系方式的数据")
            return

        filepath = Exporter.export_contacts_excel(data)
        if filepath:
            QMessageBox.information(self, "导出成功", f"已导出到: {filepath}")

    def on_bulk_import(self, urls: list):
        """批量导入URL处理"""
        if not urls:
            return

        # 创建批量爬取任务
        QMessageBox.information(
            self, "批量导入",
            f"已导入 {len(urls)} 个URL，即将开始批量爬取..."
        )

        # TODO: 实现批量URL爬取逻辑
        # 可以创建一个新的爬虫线程来处理这些URL

    def on_scheduled_task(self, task):
        """定时任务执行回调"""
        logger.info(f"执行定时任务: {task.keyword}")
        # 在主线程中启动爬取
        params = {
            "keyword": task.keyword,
            "platforms": task.platforms,
            "max_pages": 5,
            "max_comments": 50,
        }
        self.start_crawl(params)

    def show_settings(self):
        """显示设置对话框"""
        dialog = SettingsDialog(self)
        dialog.exec()

    def check_update(self):
        """检查更新"""
        dialog = UpdateDialog(self, auto_check=False)
        dialog.exec()

    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            f"跨平台评论采集与客户信息提取工具\n\n"
            f"版本: {__version__}\n"
            "功能: 自动采集抖音、小红书、快手评论\n"
            "      提取客户联系方式和购买意向\n\n"
            "技术支持: Python + Playwright + PyQt6"
        )

    def load_history_data(self):
        """加载历史数据"""
        try:
            data = self.db.get_comments(limit=1000)
            if data:
                self.result_table.load_data(data)
                self.status_bar.showMessage(f"已加载 {len(data)} 条历史数据")
        except Exception as e:
            logger.error(f"加载历史数据失败: {e}")

    def closeEvent(self, event):
        """关闭事件"""
        if self.crawler_thread and self.crawler_thread.isRunning():
            reply = QMessageBox.question(
                self, "确认退出",
                "爬虫正在运行，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return

            self.crawler_thread.stop()
            self.crawler_thread.wait()

        # 停止定时任务调度器
        self.scheduler.stop()

        self.db.close()
        event.accept()
