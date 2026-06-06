"""
数据分析模块
提供关键词统计、高频词分析、用户活跃度分析等功能
"""
import re
from collections import Counter
from typing import List, Dict, Tuple
from utils.logger import logger


class DataAnalyzer:
    """数据分析器"""

    @staticmethod
    def extract_keywords(texts: List[str], top_n: int = 20) -> List[Tuple[str, int]]:
        """
        提取高频关键词
        Args:
            texts: 文本列表
            top_n: 返回前N个关键词
        Returns:
            [(关键词, 频次), ...]
        """
        # 中文分词（简单实现：按标点和空格分割）
        words = []
        for text in texts:
            # 移除标点和特殊字符
            clean_text = re.sub(r'[^\w\s]', ' ', text)
            # 分割单词
            for word in clean_text.split():
                if len(word) >= 2:  # 过滤单字
                    words.append(word)

        # 统计词频
        word_counts = Counter(words)
        return word_counts.most_common(top_n)

    @staticmethod
    def analyze_user_activity(comments: List[dict]) -> Dict:
        """
        分析用户活跃度
        Args:
            comments: 评论列表
        Returns:
            用户活跃度统计
        """
        user_counts = Counter()
        for comment in comments:
            author = comment.get("author", "")
            if author:
                user_counts[author] += 1

        # 统计
        total_users = len(user_counts)
        active_users = sum(1 for count in user_counts.values() if count >= 3)
        top_users = user_counts.most_common(10)

        return {
            "total_users": total_users,
            "active_users": active_users,
            "top_users": top_users,
            "avg_comments_per_user": sum(user_counts.values()) / total_users if total_users > 0 else 0,
        }

    @staticmethod
    def analyze_contact_distribution(comments: List[dict]) -> Dict:
        """
        分析联系方式分布
        Args:
            comments: 评论列表
        Returns:
            联系方式分布统计
        """
        phone_count = sum(1 for c in comments if c.get("phone"))
        wechat_count = sum(1 for c in comments if c.get("wechat"))
        qq_count = sum(1 for c in comments if c.get("qq"))
        email_count = sum(1 for c in comments if c.get("email"))
        any_contact = sum(1 for c in comments if c.get("phone") or c.get("wechat") or c.get("qq") or c.get("email"))

        return {
            "total": len(comments),
            "with_contact": any_contact,
            "phone": phone_count,
            "wechat": wechat_count,
            "qq": qq_count,
            "email": email_count,
            "contact_rate": any_contact / len(comments) * 100 if comments else 0,
        }

    @staticmethod
    def analyze_intent_distribution(comments: List[dict]) -> Dict:
        """
        分析意向度分布
        Args:
            comments: 评论列表
        Returns:
            意向度分布统计
        """
        intent_counts = Counter()
        for comment in comments:
            intent = comment.get("intent", "低")
            intent_counts[intent] += 1

        return {
            "高": intent_counts.get("高", 0),
            "中": intent_counts.get("中", 0),
            "低": intent_counts.get("低", 0),
        }

    @staticmethod
    def analyze_time_distribution(comments: List[dict]) -> Dict:
        """
        分析时间分布
        Args:
            comments: 评论列表
        Returns:
            时间分布统计
        """
        hour_counts = Counter()
        for comment in comments:
            time_str = comment.get("time", "")
            if time_str:
                # 尝试提取小时
                try:
                    if ":" in time_str:
                        hour = int(time_str.split(":")[0])
                        hour_counts[hour] += 1
                except:
                    pass

        return dict(sorted(hour_counts.items()))

    @staticmethod
    def generate_summary(comments: List[dict]) -> Dict:
        """
        生成数据摘要
        Args:
            comments: 评论列表
        Returns:
            数据摘要
        """
        if not comments:
            return {
                "total": 0,
                "platforms": {},
                "intents": {},
                "contacts": {},
                "users": {},
            }

        # 平台分布
        platform_counts = Counter(c.get("platform", "") for c in comments)

        # 意向度分布
        intent_dist = DataAnalyzer.analyze_intent_distribution(comments)

        # 联系方式分布
        contact_dist = DataAnalyzer.analyze_contact_distribution(comments)

        # 用户活跃度
        user_activity = DataAnalyzer.analyze_user_activity(comments)

        # 高频关键词
        texts = [c.get("content", "") for c in comments]
        keywords = DataAnalyzer.extract_keywords(texts, top_n=10)

        return {
            "total": len(comments),
            "platforms": dict(platform_counts),
            "intents": intent_dist,
            "contacts": contact_dist,
            "users": user_activity,
            "keywords": keywords,
        }
