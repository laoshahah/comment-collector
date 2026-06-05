"""
SQLite 数据库操作
"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from config import DB_PATH
from crawlers.base_crawler import CommentData
from utils.logger import logger


class Database:
    """SQLite 数据库管理"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.init_db()

    def init_db(self):
        """初始化数据库"""
        try:
            self.conn = sqlite3.connect(str(self.db_path))
            self.conn.row_factory = sqlite3.Row
            self._create_tables()
            logger.info(f"数据库初始化完成: {self.db_path}")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    def _create_tables(self):
        """创建数据表"""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                title TEXT,
                content TEXT NOT NULL,
                author TEXT,
                phone TEXT,
                wechat TEXT,
                qq TEXT,
                intent TEXT DEFAULT '低',
                time TEXT,
                url TEXT,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, author, content)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                platforms TEXT,
                status TEXT DEFAULT 'pending',
                total_comments INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_platform ON comments(platform)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_intent ON comments(intent)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_phone ON comments(phone)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_comments_wechat ON comments(wechat)")

        self.conn.commit()

    def insert_comment(self, comment: CommentData) -> bool:
        """
        插入单条评论
        Returns:
            是否成功插入（False 表示重复）
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO comments
                (platform, title, content, author, phone, wechat, qq, intent, time, url, likes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comment.platform,
                comment.title,
                comment.content,
                comment.author,
                comment.phone,
                comment.wechat,
                comment.qq,
                comment.intent,
                comment.time,
                comment.url,
                comment.likes,
            ))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"插入评论失败: {e}")
            return False

    def insert_comments(self, comments: List[CommentData]) -> int:
        """
        批量插入评论
        Returns:
            成功插入的数量
        """
        count = 0
        for comment in comments:
            if self.insert_comment(comment):
                count += 1
        logger.info(f"批量插入评论: {count}/{len(comments)} 条")
        return count

    def get_comments(
        self,
        platform: str = None,
        intent: str = None,
        has_contact: bool = False,
        keyword: str = None,
        limit: int = 1000,
        offset: int = 0,
    ) -> List[dict]:
        """
        查询评论
        Args:
            platform: 平台筛选
            intent: 意向度筛选
            has_contact: 是否只返回有联系方式的
            keyword: 内容关键词
            limit: 返回数量限制
            offset: 偏移量
        Returns:
            评论字典列表
        """
        query = "SELECT * FROM comments WHERE 1=1"
        params = []

        if platform:
            query += " AND platform = ?"
            params.append(platform)

        if intent:
            query += " AND intent = ?"
            params.append(intent)

        if has_contact:
            query += " AND (phone != '' OR wechat != '' OR qq != '')"

        if keyword:
            query += " AND content LIKE ?"
            params.append(f"%{keyword}%")

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = self.conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_statistics(self) -> dict:
        """获取统计信息"""
        cursor = self.conn.cursor()

        # 总评论数
        cursor.execute("SELECT COUNT(*) FROM comments")
        total = cursor.fetchone()[0]

        # 各平台数量
        cursor.execute("SELECT platform, COUNT(*) FROM comments GROUP BY platform")
        platforms = {row[0]: row[1] for row in cursor.fetchall()}

        # 各意向度数量
        cursor.execute("SELECT intent, COUNT(*) FROM comments GROUP BY intent")
        intents = {row[0]: row[1] for row in cursor.fetchall()}

        # 有联系方式的数量
        cursor.execute("SELECT COUNT(*) FROM comments WHERE phone != '' OR wechat != '' OR qq != ''")
        with_contact = cursor.fetchone()[0]

        return {
            "total": total,
            "platforms": platforms,
            "intents": intents,
            "with_contact": with_contact,
        }

    def insert_task(self, keyword: str, platforms: str) -> int:
        """
        插入任务记录
        Returns:
            任务ID
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (keyword, platforms, status)
                VALUES (?, ?, 'running')
            """, (keyword, platforms))
            self.conn.commit()
            return cursor.lastrowid
        except Exception as e:
            logger.error(f"插入任务失败: {e}")
            return -1

    def update_task_status(self, task_id: int, status: str, total_comments: int = 0):
        """更新任务状态"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE tasks SET status = ?, total_comments = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, total_comments, task_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"更新任务状态失败: {e}")

    def insert_comments_batch(self, comments: List[dict]) -> int:
        """
        批量插入评论（字典格式）
        Returns:
            成功插入的数量
        """
        count = 0
        for comment_data in comments:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO comments
                    (platform, title, content, author, phone, wechat, qq, intent, time, url, likes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comment_data.get("platform", ""),
                    comment_data.get("title", ""),
                    comment_data.get("content", ""),
                    comment_data.get("author", ""),
                    comment_data.get("phone", ""),
                    comment_data.get("wechat", ""),
                    comment_data.get("qq", ""),
                    comment_data.get("intent", "低"),
                    comment_data.get("time", ""),
                    comment_data.get("url", ""),
                    comment_data.get("likes", 0),
                ))
                if cursor.rowcount > 0:
                    count += 1
            except Exception as e:
                logger.debug(f"插入评论失败: {e}")
                continue

        self.conn.commit()
        logger.info(f"批量插入评论: {count}/{len(comments)} 条")
        return count

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
