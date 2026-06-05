"""
评论解析模块
"""
from typing import List, Optional
from crawlers.base_crawler import CommentData
from utils.logger import logger
from utils.helpers import clean_text


class CommentParser:
    """评论解析器"""

    @staticmethod
    def parse_comment(raw_comment: dict, platform: str) -> Optional[CommentData]:
        """
        解析原始评论数据
        Args:
            raw_comment: 原始评论字典
            platform: 平台名称
        Returns:
            CommentData 对象或 None
        """
        try:
            content = clean_text(raw_comment.get("content", ""))
            if not content:
                return None

            return CommentData(
                platform=platform,
                title=clean_text(raw_comment.get("title", "")),
                content=content,
                author=clean_text(raw_comment.get("author", "")),
                time=raw_comment.get("time", ""),
                url=raw_comment.get("url", ""),
                likes=int(raw_comment.get("likes", 0)),
            )
        except Exception as e:
            logger.debug(f"解析评论失败: {e}")
            return None

    @staticmethod
    def filter_invalid_comments(comments: List[CommentData]) -> List[CommentData]:
        """
        过滤无效评论
        Args:
            comments: 评论列表
        Returns:
            过滤后的评论列表
        """
        filtered = []
        for comment in comments:
            # 跳过空评论
            if not comment.content or len(comment.content.strip()) < 2:
                continue

            # 跳过纯表情/符号评论
            if all(c in '😀😃😄😁😆😅🤣😂🙂🙃😉😊😇🥰😍🤩😘😗☺😚😙🥲😋😛😜🤪😝🤑🤗🤭🤫🤔🤐🤨😐😑😶😏😒🙄😬🤥😌😔😪🤤😴😷🤒🤕🤢🤮🤧🥵🥶🥴😵🤯🤠🥳🥸😎🤓🧐😕😟🙁☹😮😯😲😳🥺😦😧😨😰😥😢😭😱😖😣😞😓😩😫🥱😤😡😠🤬' for c in comment.content):
                continue

            # 跳过明显的广告/水军评论
            spam_keywords = ["加我", "免费领", "点击链接", "扫码", "优惠券", "折扣"]
            if any(kw in comment.content for kw in spam_keywords) and len(comment.content) < 20:
                continue

            filtered.append(comment)

        logger.info(f"过滤无效评论: {len(comments)} -> {len(filtered)}")
        return filtered

    @staticmethod
    def deduplicate_comments(comments: List[CommentData]) -> List[CommentData]:
        """
        评论去重
        Args:
            comments: 评论列表
        Returns:
            去重后的评论列表
        """
        seen = set()
        unique = []

        for comment in comments:
            # 使用平台+作者+内容前50字作为去重键
            key = f"{comment.platform}|{comment.author}|{comment.content[:50]}"
            if key not in seen:
                seen.add(key)
                unique.append(comment)

        logger.info(f"评论去重: {len(comments)} -> {len(unique)}")
        return unique
