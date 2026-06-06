"""
数据导出模块
支持多种导出格式和自定义列
"""
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from config import EXPORT_DIR, EXPORT_CONFIG
from utils.logger import logger


class Exporter:
    """数据导出器"""

    # 导出列定义
    COLUMNS = [
        "platform",      # 平台
        "title",         # 视频/帖子标题
        "content",       # 评论内容
        "author",        # 评论作者
        "phone",         # 手机号
        "wechat",        # 微信号
        "qq",            # QQ号
        "email",         # 邮箱
        "intent",        # 意向度
        "time",          # 评论时间
        "url",           # 原文链接
        "likes",         # 点赞数
    ]

    # 列中文名映射
    COLUMN_NAMES = {
        "platform": "平台",
        "title": "视频标题",
        "content": "评论内容",
        "author": "客户昵称",
        "phone": "手机号",
        "wechat": "微信号",
        "qq": "QQ号",
        "email": "邮箱",
        "intent": "意向度",
        "time": "时间",
        "url": "链接",
        "likes": "点赞数",
    }

    @classmethod
    def export_excel(
        cls,
        data: List[dict],
        filename: str = None,
        include_all_columns: bool = True,
    ) -> str:
        """
        导出为 Excel 文件
        Args:
            data: 评论数据列表
            filename: 文件名（不含扩展名）
            include_all_columns: 是否包含所有列
        Returns:
            导出文件路径
        """
        if not data:
            logger.warning("没有数据可导出")
            return ""

        # 生成文件名
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"评论数据_{timestamp}"

        filepath = EXPORT_DIR / f"{filename}.xlsx"

        # 创建 DataFrame
        df = pd.DataFrame(data)

        # 选择列
        if include_all_columns:
            columns = [col for col in cls.COLUMNS if col in df.columns]
            df = df[columns]

        # 重命名列
        df = df.rename(columns=cls.COLUMN_NAMES)

        # 导出
        try:
            df.to_excel(str(filepath), index=False, engine=EXPORT_CONFIG["excel_engine"])
            logger.info(f"导出 Excel 成功: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"导出 Excel 失败: {e}")
            return ""

    @classmethod
    def export_csv(
        cls,
        data: List[dict],
        filename: str = None,
    ) -> str:
        """
        导出为 CSV 文件
        Args:
            data: 评论数据列表
            filename: 文件名（不含扩展名）
        Returns:
            导出文件路径
        """
        if not data:
            logger.warning("没有数据可导出")
            return ""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"评论数据_{timestamp}"

        filepath = EXPORT_DIR / f"{filename}.csv"

        df = pd.DataFrame(data)
        columns = [col for col in cls.COLUMNS if col in df.columns]
        df = df[columns]
        df = df.rename(columns=cls.COLUMN_NAMES)

        try:
            df.to_csv(str(filepath), index=False, encoding="utf-8-sig")
            logger.info(f"导出 CSV 成功: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"导出 CSV 失败: {e}")
            return ""

    @classmethod
    def export_contacts_excel(
        cls,
        data: List[dict],
        filename: str = None,
    ) -> str:
        """
        导出仅包含联系方式的 Excel
        """
        # 筛选有联系方式的数据
        contact_data = [
            row for row in data
            if row.get("phone") or row.get("wechat") or row.get("qq") or row.get("email")
        ]

        if not contact_data:
            logger.warning("没有包含联系方式的数据")
            return ""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"客户联系方式_{timestamp}"

        return cls.export_excel(contact_data, filename)

    @classmethod
    def export_json(
        cls,
        data: List[dict],
        filename: str = None,
    ) -> str:
        """
        导出为 JSON 文件
        Args:
            data: 评论数据列表
            filename: 文件名（不含扩展名）
        Returns:
            导出文件路径
        """
        if not data:
            logger.warning("没有数据可导出")
            return ""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"评论数据_{timestamp}"

        filepath = EXPORT_DIR / f"{filename}.json"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info(f"导出 JSON 成功: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"导出 JSON 失败: {e}")
            return ""

    @classmethod
    def export_high_intent(
        cls,
        data: List[dict],
        filename: str = None,
    ) -> str:
        """
        导出高意向客户
        """
        high_intent_data = [row for row in data if row.get("intent") == "高"]

        if not high_intent_data:
            logger.warning("没有高意向客户数据")
            return ""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"高意向客户_{timestamp}"

        return cls.export_excel(high_intent_data, filename)

    @classmethod
    def export_by_platform(
        cls,
        data: List[dict],
        platform: str,
        filename: str = None,
    ) -> str:
        """
        按平台导出数据
        """
        platform_data = [row for row in data if row.get("platform") == platform]

        if not platform_data:
            logger.warning(f"没有 {platform} 的数据")
            return ""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{platform}_评论_{timestamp}"

        return cls.export_excel(platform_data, filename)
