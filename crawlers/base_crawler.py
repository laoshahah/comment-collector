"""
爬虫基类 - 定义统一接口
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from utils.logger import logger


@dataclass
class CommentData:
    """评论数据结构"""
    platform: str           # 平台名称
    title: str              # 视频/帖子标题
    content: str            # 评论内容
    author: str             # 评论作者
    time: str               # 评论时间
    url: str                # 原文链接
    likes: int = 0          # 点赞数
    phone: str = ""         # 手机号
    wechat: str = ""        # 微信号
    qq: str = ""            # QQ号
    email: str = ""         # 邮箱
    intent: str = "低"      # 意向度：高/中/低
    raw_data: dict = field(default_factory=dict)  # 原始数据


class BaseCrawler(ABC):
    """爬虫基类"""

    def __init__(self):
        self.platform_name = ""
        self.browser = None
        self.context = None
        self.page = None

    @abstractmethod
    async def search(self, keyword: str, max_pages: int = 5) -> List[dict]:
        """
        搜索内容
        Args:
            keyword: 搜索关键词
            max_pages: 最大页数
        Returns:
            内容列表 [{title, url, author, time}]
        """
        pass

    @abstractmethod
    async def get_comments(self, url: str, max_count: int = 100) -> List[CommentData]:
        """
        获取评论
        Args:
            url: 内容链接
            max_count: 最大评论数
        Returns:
            评论数据列表
        """
        pass

    async def init_browser(self, playwright):
        """初始化浏览器"""
        from crawlers.anti_detect import AntiDetect
        from config import CRAWLER_CONFIG
        from storage.cookie_manager import CookieManager

        self.browser = await playwright.chromium.launch(
            headless=CRAWLER_CONFIG["headless"]
        )
        self.context = await AntiDetect.setup_browser_context(self.browser)

        # 尝试加载保存的 Cookie
        platform_key = self.platform_name.lower().replace("站", "").replace("书", "")
        await CookieManager.apply_cookies(self.context, platform_key)

        self.page = await self.context.new_page()
        logger.info(f"{self.platform_name} 浏览器初始化完成")

    async def close(self):
        """关闭浏览器"""
        from storage.cookie_manager import CookieManager

        # 保存 Cookie
        if self.context:
            platform_key = self.platform_name.lower().replace("站", "").replace("书", "")
            await CookieManager.save_cookies(self.context, platform_key)
            await self.context.close()
        if self.browser:
            await self.browser.close()
        logger.info(f"{self.platform_name} 浏览器已关闭")

    async def safe_goto(self, url: str, timeout: int = 30000):
        """安全访问页面"""
        from utils.helpers import random_delay
        try:
            await self.page.goto(url, wait_until="domcontentloaded", timeout=timeout)
            await random_delay(1, 3)
        except Exception as e:
            logger.error(f"访问页面失败: {url}, 错误: {e}")
            raise

    async def safe_click(self, selector: str):
        """安全点击元素"""
        from utils.helpers import random_delay
        try:
            await self.page.click(selector)
            await random_delay(0.5, 1.5)
        except Exception as e:
            logger.warning(f"点击元素失败: {selector}, 错误: {e}")

    async def scroll_and_load(self, max_scrolls: int = 5):
        """滚动加载更多内容"""
        from crawlers.anti_detect import AntiDetect
        await AntiDetect.human_like_scroll(self.page, max_scrolls)
