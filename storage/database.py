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
            # check_same_thread=False 允许多线程访问
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            # 启用 WAL 模式提高并发性能
            self.conn.execute("PRAGMA journal_mode=WAL")
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
                email TEXT,
                intent TEXT DEFAULT '低',
                time TEXT,
                url TEXT,
                likes INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, author, content)
            )
        """)

        # 检查是否需要添加 email 列（兼容旧数据库）
        cursor.execute("PRAGMA table_info(comments)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'email' not in columns:
            try:
                cursor.execute("ALTER TABLE comments ADD COLUMN email TEXT DEFAULT ''")
                logger.info("已添加 email 列到数据库")
            except Exception as e:
                logger.debug(f"添加 email 列失败（可能已存在）: {e}")

        # 搜索历史表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                platforms TEXT,
                search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 批量URL表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bulk_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                platform TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                (platform, title, content, author, phone, wechat, qq, email, intent, time, url, likes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                comment.platform,
                comment.title,
                comment.content,
                comment.author,
                comment.phone,
                comment.wechat,
                comment.qq,
                comment.email,
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

        # 有联系方式的数量（包括邮箱）
        cursor.execute("SELECT COUNT(*) FROM comments WHERE phone != '' OR wechat != '' OR qq != '' OR email != ''")
        with_contact = cursor.fetchone()[0]

        # 各类型联系方式数量
        cursor.execute("SELECT COUNT(*) FROM comments WHERE phone != ''")
        with_phone = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM comments WHERE wechat != ''")
        with_wechat = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM comments WHERE qq != ''")
        with_qq = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM comments WHERE email != ''")
        with_email = cursor.fetchone()[0]

        return {
            "total": total,
            "platforms": platforms,
            "intents": intents,
            "with_contact": with_contact,
            "with_phone": with_phone,
            "with_wechat": with_wechat,
            "with_qq": with_qq,
            "with_email": with_email,
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
        批量插入评论（字典格式）- 使用事务和 executemany 优化
        Returns:
            成功插入的数量
        """
        if not comments:
            return 0

        # 准备数据
        data = [
            (
                c.get("platform", ""),
                c.get("title", ""),
                c.get("content", ""),
                c.get("author", ""),
                c.get("phone", ""),
                c.get("wechat", ""),
                c.get("qq", ""),
                c.get("email", ""),
                c.get("intent", "低"),
                c.get("time", ""),
                c.get("url", ""),
                c.get("likes", 0),
            )
            for c in comments
        ]

        try:
            cursor = self.conn.cursor()
            # 使用事务批量插入
            cursor.execute("BEGIN TRANSACTION")
            cursor.executemany("""
                INSERT OR IGNORE INTO comments
                (platform, title, content, author, phone, wechat, qq, email, intent, time, url, likes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, data)
            count = cursor.rowcount
            cursor.execute("COMMIT")

            logger.info(f"批量插入评论: {count}/{len(comments)} 条")
            return count
        except Exception as e:
            logger.error(f"批量插入失败: {e}")
            try:
                cursor.execute("ROLLBACK")
            except:
                pass
            return 0

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

    def add_search_history(self, keyword: str, platforms: str):
        """添加搜索历史"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO search_history (keyword, platforms)
                VALUES (?, ?)
            """, (keyword, platforms))
            self.conn.commit()
        except Exception as e:
            logger.error(f"添加搜索历史失败: {e}")

    def get_search_history(self, limit: int = 20) -> List[dict]:
        """获取搜索历史"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM search_history
                ORDER BY search_time DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取搜索历史失败: {e}")
            return []

    def delete_search_history(self, history_id: int):
        """删除搜索历史"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM search_history WHERE id = ?", (history_id,))
            self.conn.commit()
        except Exception as e:
            logger.error(f"删除搜索历史失败: {e}")

    def clear_search_history(self):
        """清空搜索历史"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM search_history")
            self.conn.commit()
        except Exception as e:
            logger.error(f"清空搜索历史失败: {e}")

    def add_bulk_urls(self, urls: List[str], platform: str = ""):
        """批量添加URL"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            for url in urls:
                cursor.execute("""
                    INSERT INTO bulk_urls (url, platform)
                    VALUES (?, ?)
                """, (url, platform))
            cursor.execute("COMMIT")
            logger.info(f"批量添加 {len(urls)} 个URL")
        except Exception as e:
            logger.error(f"批量添加URL失败: {e}")
            try:
                cursor.execute("ROLLBACK")
            except:
                pass

    def get_pending_urls(self, limit: int = 100) -> List[dict]:
        """获取待处理的URL"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                SELECT * FROM bulk_urls
                WHERE status = 'pending'
                ORDER BY created_at ASC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"获取待处理URL失败: {e}")
            return []

    def update_url_status(self, url_id: int, status: str):
        """更新URL状态"""
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                UPDATE bulk_urls SET status = ? WHERE id = ?
            """, (status, url_id))
            self.conn.commit()
        except Exception as e:
            logger.error(f"更新URL状态失败: {e}")
