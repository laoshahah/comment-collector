"""
通用工具函数
"""
import random
import asyncio
from datetime import datetime, timedelta
from config import USER_AGENTS, CRAWLER_CONFIG


def get_random_ua() -> str:
    """获取随机 User-Agent"""
    return random.choice(USER_AGENTS)


def get_random_headers() -> dict:
    """获取随机请求头"""
    return {
        "User-Agent": get_random_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


async def random_delay(min_sec: float = None, max_sec: float = None):
    """随机延时"""
    min_sec = min_sec or CRAWLER_CONFIG["min_delay"]
    max_sec = max_sec or CRAWLER_CONFIG["max_delay"]
    delay = random.uniform(min_sec, max_sec)
    await asyncio.sleep(delay)


def format_time(time_str: str) -> str:
    """格式化时间字符串"""
    if not time_str:
        return ""
    # 尝试解析常见时间格式
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m-%d %H:%M"]:
        try:
            dt = datetime.strptime(time_str.strip(), fmt)
            return dt.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            continue
    return time_str.strip()


def truncate_text(text: str, max_length: int = 100) -> str:
    """截断文本"""
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def clean_text(text: str) -> str:
    """清洗文本（去除多余空白、特殊字符）"""
    if not text:
        return ""
    import re
    # 去除多余空白
    text = re.sub(r'\s+', ' ', text)
    # 去除首尾空白
    text = text.strip()
    return text
