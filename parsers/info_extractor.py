"""
客户信息提取模块
"""
import re
from typing import List, Tuple
from crawlers.base_crawler import CommentData
from config import EXTRACTION_CONFIG
from utils.logger import logger


class InfoExtractor:
    """客户信息提取器"""

    # 手机号正则（中国大陆）
    PHONE_RE = re.compile(r'1[3-9]\d{9}')

    # 微信号正则
    WECHAT_RE = re.compile(
        r'(?:[Vv][Xx]|微信|WX|wx|WeChat|wechat)[:：\s]*([a-zA-Z0-9_]{5,20})'
    )

    # QQ号正则
    QQ_RE = re.compile(
        r'[Qq]{2}[:：\s]*([1-9]\d{4,11})'
    )

    # 邮箱正则
    EMAIL_RE = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    )

    @classmethod
    def extract_phone(cls, text: str) -> str:
        """提取手机号"""
        matches = cls.PHONE_RE.findall(text)
        return matches[0] if matches else ""

    @classmethod
    def extract_wechat(cls, text: str) -> str:
        """提取微信号"""
        match = cls.WECHAT_RE.search(text)
        return match.group(1) if match else ""

    @classmethod
    def extract_qq(cls, text: str) -> str:
        """提取QQ号"""
        match = cls.QQ_RE.search(text)
        return match.group(1) if match else ""

    @classmethod
    def extract_email(cls, text: str) -> str:
        """提取邮箱"""
        match = cls.EMAIL_RE.search(text)
        return match.group(0) if match else ""

    @classmethod
    def has_contact_info(cls, text: str) -> bool:
        """检查是否包含联系方式"""
        return bool(
            cls.PHONE_RE.search(text) or
            cls.WECHAT_RE.search(text) or
            cls.QQ_RE.search(text) or
            cls.EMAIL_RE.search(text)
        )

    @classmethod
    def has_intent_keywords(cls, text: str) -> bool:
        """检查是否包含需求关键词"""
        keywords = EXTRACTION_CONFIG["intent_keywords"]
        return any(kw in text for kw in keywords)

    @classmethod
    def judge_intent(cls, text: str) -> str:
        """
        判断意向度
        Returns:
            "高" / "中" / "低"
        """
        has_contact = cls.has_contact_info(text)
        has_intent = cls.has_intent_keywords(text)

        if has_contact and has_intent:
            return "高"
        elif has_contact or has_intent:
            return "中"
        else:
            return "低"

    @classmethod
    def extract_all(cls, comment: CommentData) -> CommentData:
        """
        提取评论中的所有客户信息
        Args:
            comment: 评论数据
        Returns:
            更新后的评论数据
        """
        text = comment.content

        # 提取联系方式
        comment.phone = cls.extract_phone(text)
        comment.wechat = cls.extract_wechat(text)
        comment.qq = cls.extract_qq(text)
        comment.email = cls.extract_email(text)

        # 判断意向度
        comment.intent = cls.judge_intent(text)

        return comment

    @classmethod
    def process_comments(cls, comments: List[CommentData]) -> List[CommentData]:
        """
        批量处理评论，提取客户信息
        Args:
            comments: 评论列表
        Returns:
            处理后的评论列表
        """
        processed = []
        for comment in comments:
            processed_comment = cls.extract_all(comment)
            processed.append(processed_comment)

        # 统计
        with_phone = sum(1 for c in processed if c.phone)
        with_wechat = sum(1 for c in processed if c.wechat)
        with_qq = sum(1 for c in processed if c.qq)
        with_email = sum(1 for c in processed if c.email)
        high_intent = sum(1 for c in processed if c.intent == "高")

        logger.info(f"信息提取完成: 手机号{with_phone}个, 微信{with_wechat}个, QQ{with_qq}个, 邮箱{with_email}个, 高意向{high_intent}条")

        return processed
