"""
反爬策略模块
"""
import random
from config import CRAWLER_CONFIG, USER_AGENTS


class AntiDetect:
    """反爬检测规避"""

    @staticmethod
    def get_random_ua() -> str:
        """获取随机 User-Agent"""
        return random.choice(USER_AGENTS)

    @staticmethod
    def get_viewport() -> dict:
        """获取随机视口大小"""
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1440, "height": 900},
            {"width": 1536, "height": 864},
        ]
        return random.choice(viewports)

    @staticmethod
    def get_locale() -> str:
        """获取随机语言"""
        locales = ["zh-CN", "zh-TW", "en-US"]
        return random.choice(locales)

    @staticmethod
    def get_timezone() -> str:
        """获取随机时区"""
        timezones = ["Asia/Shanghai", "Asia/Hong_Kong", "Asia/Taipei"]
        return random.choice(timezones)

    @classmethod
    async def setup_browser_context(cls, browser):
        """配置浏览器上下文（反爬）"""
        context = await browser.new_context(
            user_agent=cls.get_random_ua(),
            viewport=cls.get_viewport(),
            locale=cls.get_locale(),
            timezone_id=cls.get_timezone(),
            # 禁用 WebDriver 检测
            extra_http_headers={
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            },
        )

        # 注入反检测脚本
        await context.add_init_script("""
            // 隐藏 webdriver 标志
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            // 隐藏自动化工具
            window.navigator.chrome = { runtime: {} };
            // 隐藏 Playwright 特征
            delete window.__playwright;
            delete window.__pw_manual;
        """)

        return context

    @staticmethod
    async def human_like_scroll(page, scroll_count: int = 3):
        """模拟人类滚动行为"""
        for _ in range(scroll_count):
            # 随机滚动距离
            scroll_distance = random.randint(300, 800)
            await page.evaluate(f"window.scrollBy(0, {scroll_distance})")
            # 随机等待
            await page.wait_for_timeout(random.randint(500, 1500))

    @staticmethod
    async def random_mouse_move(page):
        """随机鼠标移动"""
        viewport = page.viewport_size
        if viewport:
            x = random.randint(0, viewport["width"])
            y = random.randint(0, viewport["height"])
            await page.mouse.move(x, y)
