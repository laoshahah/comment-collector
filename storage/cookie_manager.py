"""
Cookie 管理模块
保存和加载浏览器 Cookie/会话状态
"""
import json
from pathlib import Path
from typing import Optional, Dict
from config import PROJECT_ROOT
from utils.logger import logger


# Cookie 存储目录
COOKIE_DIR = PROJECT_ROOT / "cookies"
COOKIE_DIR.mkdir(parents=True, exist_ok=True)


class CookieManager:
    """Cookie 管理器"""

    @staticmethod
    def get_cookie_path(platform: str) -> Path:
        """获取平台 Cookie 文件路径"""
        return COOKIE_DIR / f"{platform}_cookies.json"

    @staticmethod
    async def save_cookies(context, platform: str) -> bool:
        """
        保存浏览器上下文的 Cookie
        Args:
            context: Playwright 浏览器上下文
            platform: 平台名称
        Returns:
            是否保存成功
        """
        try:
            # 获取 storage state（包括 cookies、localStorage 等）
            state = await context.storage_state()

            cookie_path = CookieManager.get_cookie_path(platform)
            with open(cookie_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2)

            logger.info(f"已保存 {platform} Cookie")
            return True
        except Exception as e:
            logger.error(f"保存 {platform} Cookie 失败: {e}")
            return False

    @staticmethod
    def load_cookies(platform: str) -> Optional[Dict]:
        """
        加载平台 Cookie
        Args:
            platform: 平台名称
        Returns:
            Cookie 字典或 None
        """
        try:
            cookie_path = CookieManager.get_cookie_path(platform)
            if cookie_path.exists():
                with open(cookie_path, "r", encoding="utf-8") as f:
                    state = json.load(f)
                logger.info(f"已加载 {platform} Cookie")
                return state
        except Exception as e:
            logger.error(f"加载 {platform} Cookie 失败: {e}")
        return None

    @staticmethod
    def delete_cookies(platform: str) -> bool:
        """
        删除平台 Cookie
        Args:
            platform: 平台名称
        Returns:
            是否删除成功
        """
        try:
            cookie_path = CookieManager.get_cookie_path(platform)
            if cookie_path.exists():
                cookie_path.unlink()
                logger.info(f"已删除 {platform} Cookie")
                return True
        except Exception as e:
            logger.error(f"删除 {platform} Cookie 失败: {e}")
        return False

    @staticmethod
    def has_cookies(platform: str) -> bool:
        """
        检查是否有保存的 Cookie
        Args:
            platform: 平台名称
        Returns:
            是否有 Cookie
        """
        return CookieManager.get_cookie_path(platform).exists()

    @staticmethod
    def list_saved_cookies() -> list:
        """列出所有已保存的 Cookie"""
        cookies = []
        for file in COOKIE_DIR.glob("*_cookies.json"):
            platform = file.stem.replace("_cookies", "")
            cookies.append(platform)
        return cookies

    @staticmethod
    async def apply_cookies(context, platform: str) -> bool:
        """
        应用保存的 Cookie 到浏览器上下文
        Args:
            context: Playwright 浏览器上下文
            platform: 平台名称
        Returns:
            是否应用成功
        """
        state = CookieManager.load_cookies(platform)
        if state:
            try:
                # 添加 cookies
                if "cookies" in state:
                    await context.add_cookies(state["cookies"])
                logger.info(f"已应用 {platform} Cookie")
                return True
            except Exception as e:
                logger.error(f"应用 {platform} Cookie 失败: {e}")
        return False
