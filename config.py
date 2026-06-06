"""
全局配置文件
"""
import os
import json
from pathlib import Path

# 版本号（唯一定义处）
__version__ = "1.1.0"

# 项目根目录
PROJECT_ROOT = Path(__file__).parent

# 设置文件路径
SETTINGS_FILE = PROJECT_ROOT / "settings.json"

# 数据库路径
DB_PATH = PROJECT_ROOT / "data" / "comments.db"

# 导出目录
EXPORT_DIR = PROJECT_ROOT / "exports"

# 日志目录
LOG_DIR = PROJECT_ROOT / "logs"

# 爬虫配置
CRAWLER_CONFIG = {
    # 请求延时范围（秒）
    "min_delay": 2,
    "max_delay": 5,
    # 最大爬取页数
    "max_pages": 10,
    # 每页最大评论数
    "max_comments_per_page": 20,
    # 是否无头模式（True=不显示浏览器窗口）
    "headless": False,
    # 超时时间（秒）
    "timeout": 30,
    # 代理配置（可选）
    "proxy": None,
}

# User-Agent 列表
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# 平台配置
PLATFORMS = {
    "douyin": {
        "name": "抖音",
        "search_url": "https://www.douyin.com/search/{keyword}",
        "enabled": True,
    },
    "xiaohongshu": {
        "name": "小红书",
        "search_url": "https://www.xiaohongshu.com/search_result?keyword={keyword}",
        "enabled": True,
    },
    "kuaishou": {
        "name": "快手",
        "search_url": "https://www.kuaishou.com/search/video?keyword={keyword}",
        "enabled": True,
    },
    "bilibili": {
        "name": "B站",
        "search_url": "https://search.bilibili.com/all?keyword={keyword}",
        "enabled": True,
    },
    "weibo": {
        "name": "微博",
        "search_url": "https://s.weibo.com/weibo?q={keyword}",
        "enabled": True,
    },
    "zhihu": {
        "name": "知乎",
        "search_url": "https://www.zhihu.com/search?type=content&q={keyword}",
        "enabled": True,
    },
}

# 客户信息提取配置
EXTRACTION_CONFIG = {
    # 需求关键词
    "intent_keywords": [
        "多少钱", "怎么买", "链接", "价格", "加盟", "联系方式",
        "教程", "哪里买", "怎么联系", "私聊", "加我", "求链接",
        "想要", "怎么入手", "有卖的吗", "代理", "合作",
    ],
    # 高意向关键词（包含联系方式 + 需求关键词）
    "high_intent_requires_contact": True,
}

# 导出配置
EXPORT_CONFIG = {
    "default_format": "excel",  # excel / csv
    "excel_engine": "openpyxl",
}

# 创建必要的目录
for dir_path in [DB_PATH.parent, EXPORT_DIR, LOG_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)


def load_settings() -> dict:
    """从文件加载设置"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_settings(settings: dict):
    """保存设置到文件"""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存设置失败: {e}")


# 启动时加载设置
_saved_settings = load_settings()
if _saved_settings:
    CRAWLER_CONFIG.update(_saved_settings.get("crawler", {}))
    EXPORT_CONFIG.update(_saved_settings.get("export", {}))
